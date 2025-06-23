import { useEffect, useState } from 'react';
import { firestore } from '../services/firebase';
import { collection, getDocs, addDoc, DocumentData } from 'firebase/firestore';

interface FirebaseData {
  id: string;
  [key: string]: any;
}

const useFirebase = () => {
    const [data, setData] = useState<FirebaseData[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const snapshot = await getDocs(collection(firestore, 'chatData'));
                const fetchedData: FirebaseData[] = snapshot.docs.map((doc) => ({ 
                    id: doc.id, 
                    ...doc.data() 
                }));
                setData(fetchedData);
            } catch (err) {
                setError(err as Error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const addData = async (newData: DocumentData) => {
        try {
            await addDoc(collection(firestore, 'chatData'), newData);
            setData(prevData => prevData ? [...prevData, { id: Date.now().toString(), ...newData }] : [{ id: Date.now().toString(), ...newData }]);
        } catch (err) {
            setError(err as Error);
        }
    };

    return { data, loading, error, addData };
};

export default useFirebase;