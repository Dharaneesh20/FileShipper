/**
 * Network Discovery Module
 * Helps find nearby devices on the local network for file transfer
 */
class NetworkDiscovery {
    constructor(options = {}) {
        this.options = {
            autoStart: true,
            scanInterval: 5000,
            ...options
        };
        
        this.devices = new Map();
        this.listeners = [];
        this.scanning = false;
        
        if (this.options.autoStart) {
            this.startScanning();
        }
    }
    
    startScanning() {
        if (this.scanning) return;
        
        this.scanning = true;
        this.eventSource = new EventSource('/api/scan/');
        
        this.eventSource.onmessage = (event) => {
            try {
                const devices = JSON.parse(event.data);
                this.updateDevices(devices);
            } catch (e) {
                console.error('Error parsing device data:', e);
            }
        };
        
        this.eventSource.onerror = (error) => {
            console.error('Network discovery error:', error);
            this.scanning = false;
            
            // Try to reconnect
            setTimeout(() => {
                this.startScanning();
            }, this.options.scanInterval);
        };
    }
    
    stopScanning() {
        if (this.eventSource) {
            this.eventSource.close();
            this.scanning = false;
        }
    }
    
    updateDevices(deviceList) {
        // Convert array to map for easier management
        const deviceMap = new Map();
        deviceList.forEach(device => {
            deviceMap.set(device.ip + ':' + device.port, device);
        });
        
        // Find new devices
        deviceMap.forEach((device, key) => {
            if (!this.devices.has(key)) {
                this.notifyListeners('deviceFound', device);
            }
        });
        
        // Find removed devices
        this.devices.forEach((device, key) => {
            if (!deviceMap.has(key)) {
                this.notifyListeners('deviceLost', device);
            }
        });
        
        // Update master list
        this.devices = deviceMap;
        
        // Notify about all devices
        this.notifyListeners('devicesUpdated', Array.from(this.devices.values()));
    }
    
    getDevices() {
        return Array.from(this.devices.values());
    }
    
    addListener(eventType, callback) {
        this.listeners.push({ eventType, callback });
    }
    
    notifyListeners(eventType, data) {
        this.listeners
            .filter(listener => listener.eventType === eventType)
            .forEach(listener => listener.callback(data));
    }
    
    // Manual device scan
    scan() {
        fetch('/api/devices/')
            .then(response => response.json())
            .then(devices => {
                this.updateDevices(devices);
                return devices;
            });
    }
}

// Create singleton instance
window.networkDiscovery = window.networkDiscovery || new NetworkDiscovery();
