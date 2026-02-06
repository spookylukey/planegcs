// Shim: Base/Console.h - minimal stub for FreeCAD logging
#ifndef BASE_CONSOLE_H
#define BASE_CONSOLE_H

#include <cstdio>
#include <string>

namespace Base {

class ConsoleSingleton {
public:
    template<typename... Args>
    void log(const char* fmt, Args&&... args) {
        // Uncomment for debug: fprintf(stderr, fmt, args...);
        (void)fmt;
    }
    template<typename... Args>
    void warning(const char* fmt, Args&&... args) {
        fprintf(stderr, "[WARN] ");
        fprintf(stderr, fmt, args...);
    }
    template<typename... Args>
    void log(const std::string& /*notifier*/, const char* fmt, Args&&... args) {
        (void)fmt;
    }
    template<typename... Args>
    void warning(const std::string& /*notifier*/, const char* fmt, Args&&... args) {
        fprintf(stderr, "[WARN] ");
        fprintf(stderr, fmt, args...);
    }
};

inline ConsoleSingleton& Console() {
    static ConsoleSingleton instance;
    return instance;
}

} // namespace Base

#endif // BASE_CONSOLE_H
