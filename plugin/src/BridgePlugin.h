// BridgePlugin.h — Vectorworks Voice Copilot Phase 0 skeleton
// VW_SDK: replace stubs with real VCOM interfaces from the Vectorworks SDK.
#pragma once

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <queue>
#include <string>
#include <thread>

namespace vw_voice {

struct BridgeCommand {
  std::string id;
  std::string method;
  std::string params_json;
};

struct BridgeResult {
  std::string id;
  bool ok = false;
  std::string payload_json;  // result or error object
};

// Command queue: socket thread enqueues; main/idle pump dequeues and executes.
class CommandQueue {
 public:
  void Push(BridgeCommand cmd);
  bool TryPop(BridgeCommand& out);
  void PushResult(BridgeResult result);
  bool TryPopResult(BridgeResult& out);

 private:
  std::mutex mu_;
  std::queue<BridgeCommand> cmds_;
  std::queue<BridgeResult> results_;
};

// VW_SDK TODO: Implement as a VW extension/menu command registering with VCOM.
class BridgePlugin {
 public:
  BridgePlugin();
  ~BridgePlugin();

  // Start Unix domain socket listener (mode 0600). Non-blocking accept loop on worker thread.
  bool Start(const std::string& socket_path);
  void Stop();

  // Call from VW idle / main-thread timer — NEVER from the socket thread.
  void IdlePump();

 private:
  void SocketThreadMain(std::string socket_path);
  BridgeResult DispatchOnMainThread(const BridgeCommand& cmd);

  CommandQueue queue_;
  std::atomic<bool> running_{false};
  std::thread socket_thread_;
};

}  // namespace vw_voice
