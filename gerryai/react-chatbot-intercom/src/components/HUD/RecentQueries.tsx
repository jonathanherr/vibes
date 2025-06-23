import React from 'react';

interface Query {
    id: number;
    question: string;
    answer: string;
}

interface RecentQueriesProps {
    queries: Query[];
}

const RecentQueries: React.FC<RecentQueriesProps> = ({ queries }) => {
    return (
        <div className="recent-queries">
            <h2>Recent Queries</h2>
            <ul>
                {queries.map(query => (
                    <li key={query.id}>
                        <strong>Q:</strong> {query.question} <br />
                        <strong>A:</strong> {query.answer}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default RecentQueries;