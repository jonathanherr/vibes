// Placeholder intercom service for tablet communication
export const intercomService = {
  onTabletsUpdate: (callback: (tablets: string[]) => void) => {
    // Mock implementation
    callback(['Kitchen Tablet', 'Living Room Tablet']);
    return () => {}; // unsubscribe function
  },
  
  startCall: (tabletId: string) => {
    console.log('Starting call to:', tabletId);
  },
  
  endCall: (tabletId: string) => {
    console.log('Ending call to:', tabletId);
  },
  
  sendMessage: (tabletId: string, message: string) => {
    console.log('Sending message to:', tabletId, message);
  },
  
  onMessageReceived: (callback: (message: string) => void) => {
    // Mock implementation
    return () => {}; // unsubscribe function
  }
};