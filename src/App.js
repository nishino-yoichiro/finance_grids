import React, { useState, useEffect } from 'react';
import Box from './Box';
import './App.css';

function App() {
    const [totalPnL, setTotalPnL] = useState(0);
    const [totalTrades, setTotalTrades] = useState(0);
    const [averageWinner, setAverageWinner] = useState(0);
    const [averageLoser, setAverageLoser] = useState(0);

    useEffect(() => {
        const fileName = 'orders.csv';
        fetch(`http://localhost:5000/api/pnl?file_name=${fileName}`)
            .then(response => response.json())
            .then(data => setTotalPnL(data.Total_PnL))
            .catch(error => console.error('Error fetching PnL data:', error));
    }, []);

    const gridData = [
        [
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Total P&L', value: totalPnL, totalTrades: totalTrades } },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Total P&L', value: '1234.56', totalTrades: '1'} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Total P&L', value: '1234.56', totalTrades: '1'} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'averageTrades', label: 'Average winning trade', value: '234.56', averageTrades: '17.28'} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'averageTrades', label: 'Average losing trade', value: '-234.56', averageTrades: '17.28'} },
        ],
        [
            { type: 'Daily PnL', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L" }},
            { type: 'Daily PnL', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L" }},
            { type: 'Daily PnL', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L" }},
        ],
        [
            { type: 'Calendar', width: '94vw', height: '80vw', content: { label: "Calendar" }},
        ]
    ];

    return (
        <div className="app-container">
            <div className="grid-container">
                {gridData.map((row, rowIndex) => (
                    <div className="grid-row" key={rowIndex}>
                        {row.map((box, boxIndex) => (
                            <Box
                                key={boxIndex}
                                type={box.type}
                                width={box.width}
                                height={box.height}
                                content={box.content}
                            />
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default App;