import { useState, useEffect } from 'react';
import { intercomService } from '../services/intercomService';

interface IntercomMessage {
  text: string;
  sender: string;
}

const useIntercom = () => {
    const [connectedTablets, setConnectedTablets] = useState<string[]>([]);
    const [currentCall, setCurrentCall] = useState<string | null>(null);
    const [messages, setMessages] = useState<IntercomMessage[]>([]);

    useEffect(() => {
        const unsubscribe = intercomService.onTabletsUpdate((tablets: string[]) => {
            setConnectedTablets(tablets);
        });

        return () => unsubscribe();
    }, []);

    const startCall = (tabletId: string) => {
        intercomService.startCall(tabletId);
        setCurrentCall(tabletId);
    };

    const endCall = () => {
        if (currentCall) {
            intercomService.endCall(currentCall);
            setCurrentCall(null);
        }
    };

    const sendMessage = (message: string) => {
        if (currentCall) {
            intercomService.sendMessage(currentCall, message);
            setMessages((prevMessages) => [...prevMessages, { text: message, sender: 'me' }]);
        }
    };

    const receiveMessage = (message: string) => {
        setMessages((prevMessages) => [...prevMessages, { text: message, sender: 'other' }]);
    };

    useEffect(() => {
        const unsubscribe = intercomService.onMessageReceived(receiveMessage);

        return () => unsubscribe();
    }, []);

    return {
        connectedTablets,
        currentCall,
        messages,
        startCall,
        endCall,
        sendMessage,
    };
};

export default useIntercom;