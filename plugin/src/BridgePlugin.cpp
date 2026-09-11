// BridgePlugin.cpp — Phase 0 C++ skeleton (does not link on Linux without VW_SDK).
//
// Architecture:
//   [socket worker] accept + read newline JSON → CommandQueue
//   [VW main / idle] IdlePump() → dispatch allowlisted tools → enqueue result
//   [socket worker] write response line
//
// VW_SDK TODOs:
//   - Register menu command "Start Voice Bridge" / "Stop Voice Bridge"
//   - Obtain document units / create line via VCOM or by invoking python/ helpers
//   - Ensure IdlePump is scheduled on the UI-safe path (timer / idle callback)
//
// SECURITY: Allowlist only. Do NOT add run_script / eval / arbitrary VectorScript.

#include "BridgePlugin.h"

#include <cstring>
#include <iostream>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/un.h>
#include <unistd.h>

namespace vw_voice {

void CommandQueue::Push(BridgeCommand cmd) {
  std::lock_guard<std::mutex> lock(mu_);
  cmds_.push(std::move(cmd));
}

bool CommandQueue::TryPop(BridgeCommand& out) {
  std::lock_guard<std::mutex> lock(mu_);
  if (cmds_.empty()) return false;
  out = std::move(cmds_.front());
  cmds_.pop();
  return true;
}

void CommandQueue::PushResult(BridgeResult result) {
  std::lock_guard<std::mutex> lock(mu_);
  results_.push(std::move(result));
}

bool CommandQueue::TryPopResult(BridgeResult& out) {
  std::lock_guard<std::mutex> lock(mu_);
  if (results_.empty()) return false;
  out = std::move(results_.front());
  results_.pop();
  return true;
}

BridgePlugin::BridgePlugin() = default;

BridgePlugin::~BridgePlugin() { Stop(); }

bool BridgePlugin::Start(const std::string& socket_path) {
  if (running_.exchange(true)) return true;
  socket_thread_ = std::thread(&BridgePlugin::SocketThreadMain, this, socket_path);
  return true;
}

void BridgePlugin::Stop() {
  if (!running_.exchange(false)) return;
  if (socket_thread_.joinable()) socket_thread_.join();
}

void BridgePlugin::IdlePump() {
  // VW_SDK TODO: invoke only on main/UI thread.
  BridgeCommand cmd;
  while (queue_.TryPop(cmd)) {
    BridgeResult result = DispatchOnMainThread(cmd);
    queue_.PushResult(std::move(result));
  }
}

BridgeResult BridgePlugin::DispatchOnMainThread(const BridgeCommand& cmd) {
  BridgeResult result;
  result.id = cmd.id;

  // Allowlist — mirror bridge/tools.py. No run_script / eval.
  if (cmd.method == "ping") {
    result.ok = true;
    result.payload_json = "{\"pong\":true}";
    return result;
  }
  if (cmd.method == "get_document_info") {
    // VW_SDK TODO: call python helper or VCOM for real units / name / version.
    result.ok = true;
    result.payload_json =
        "{\"name\":\"TODO\",\"units\":\"inches\",\"vw_version\":\"2026\",\"mock\":false}";
    return result;
  }
  if (cmd.method == "get_selection") {
    // VW_SDK TODO: summarize selection via vs / VCOM.
    result.ok = true;
    result.payload_json = "{\"count\":0,\"objects\":[]}";
    return result;
  }
  if (cmd.method == "create_line") {
    // VW_SDK TODO: parse params_json; call plugin/python/create_line.py helper via VW.
    // Coordinates are document inches.
    result.ok = true;
    result.payload_json = "{\"handle\":\"TODO\",\"length_inches\":0}";
    return result;
  }

  result.ok = false;
  result.payload_json =
      "{\"code\":\"unknown_method\",\"message\":\"method not allowlisted\"}";
  return result;
}

void BridgePlugin::SocketThreadMain(std::string socket_path) {
  // Minimal accept loop sketch. Production: non-blocking, per-client buffers, result wait.
  unlink(socket_path.c_str());
  int fd = ::socket(AF_UNIX, SOCK_STREAM, 0);
  if (fd < 0) {
    running_ = false;
    return;
  }
  sockaddr_un addr{};
  addr.sun_family = AF_UNIX;
  std::strncpy(addr.sun_path, socket_path.c_str(), sizeof(addr.sun_path) - 1);
  if (bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
    close(fd);
    running_ = false;
    return;
  }
  // SECURITY: owner-only socket.
  chmod(socket_path.c_str(), S_IRUSR | S_IWUSR);
  listen(fd, 8);

  // VW_SDK TODO: integrate with IdlePump result delivery to connected clients.
  while (running_) {
    // Placeholder accept — full NDJSON framing implemented in Python bridge for Phase 0 mock.
    usleep(100000);
  }
  close(fd);
  unlink(socket_path.c_str());
}

}  // namespace vw_voice
