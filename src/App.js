import React, { useState, useEffect } from 'react';
import Box from './Box';
import './App.css';
import { data } from 'autoprefixer';

function App() {
    const [totalPnL, setTotalPnL] = useState(0);
    const [totalTrades, setTotalTrades] = useState(0);
    const [averageWinner, setAverageWinner] = useState(0);
    const [totalTradesWinner, setTotalTradesWinner] = useState(0);
    const [averageLoser, setAverageLoser] = useState(0);
    const [totalTradesLoser, setTotalTradesLoser] = useState(0);
    const [averageContractSize, setAverageContractSize] = useState(0);
    const [averageContractSizeChange, setAverageContractSizeChange] = useState(0);

    useEffect(() => {
        const fileName = 'orders.csv';
        fetch(`http://localhost:5000/api/pnl?file_name=${fileName}`)
            .then(response => response.json())
            .then(data => {
                setTotalPnL(data.Total_PnL)
                setTotalTrades(data.Total_Trades)
                setAverageWinner(data.Average_Winner)
                setTotalTradesWinner(data.Average_Winner_Total_Trades)
                setAverageLoser(data.Average_Loser)
                setTotalTradesLoser(data.Average_Loser_Total_Trades)
                setAverageContractSize(data.Average_Contract_Size)
                setAverageContractSizeChange(data.Average_Contract_Size_Change)
            })
            .catch(error => console.error('Error fetching PnL data:', error));
    }, []);

    const gridData = [
        [
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Overall P&L', value: totalPnL, totalTrades: totalTrades } },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Average Winner', value: averageWinner, totalTrades: totalTradesWinner} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'totalTrades', label: 'Average Loser', value: averageLoser, totalTrades: totalTradesLoser} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'averageCons', label: 'Average contract size', value: averageContractSize, averageTrades: averageContractSizeChange} },
            { type: 'box-net-profit-loss', width: '18vw', height: '6vw', content: { variation: 'profitFactor', label: 'Profit Factor', value: Math.round(averageWinner/averageLoser * 100) / 100} },
        ],
        [
            { type: 'Charts', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L", dataType: 'Cumulative_PnL' }},
            { type: 'Charts', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L", dataType: 'PnL_By_Day'}},
            { type: 'Charts', width: '30vw', height: '30vw', content: { label: "Daily Net Cumulative P&L" }},
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