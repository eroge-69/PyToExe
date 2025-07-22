#include <iostream>
#include <functional>
#include <vector>

struct DeviceFilter {
    int vendorId;
    int productId;
};

class MyButton {
public:
    void addEventListener(const std::string& eventType, std::function<void()> callback) {
        // Simulate adding an event listener
        if (eventType == "click") {
            callback();
        }
    }
};

void requestDevice(const std::vector<DeviceFilter>& filters) {
    // Simulate the requestDevice functionality
    std::cout << "Requesting device with filters:\n";
    for (const auto& filter : filters) {
        std::cout << "Vendor ID: " << std::hex << filter.vendorId << ", Product ID: " << std::hex << filter.productId << std::dec << std::endl;
    }
}

void sendMessage(const std::string& message) {
    // Simulate sending a message
    std::cout << "Sending message: " << message << std::endl;
}

int main() {
    MyButton myButton;

    myButton.addEventListener("click", [&]() {
        requestDevice({ { 0x1234, 0x5678 } });
        sendMessage("newDevice");
    });

    return 0;
}