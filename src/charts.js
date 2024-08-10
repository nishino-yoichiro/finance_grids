import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const Chart = () => {
    const chartContainerRef = useRef(null);

    useEffect(() => {
        const chartOptions = {
            layout: {
                textColor: '#A4A5AA',
                background: { type: 'solid', color: '#141a1e' },
            },
            grid: {
                vertLines: {
                    visible: false,
                },
                horzLines: {
                    color: '#2B2B43',
                },
            }
        };
        const chart = createChart(chartContainerRef.current, chartOptions);
        
        const areaSeries = chart.addAreaSeries({
            lineColor: '#2962FF',
            topColor: '#2962FF',
            bottomColor: 'rgba(41, 98, 255, 0.28)',
        });

        const fileName = 'orders.csv';
        fetch(`http://localhost:5000/api/pnl?file_name=${fileName}`)
            .then(response => response.json())
            .then(data => {
                const formattedData = Object.keys(data.Cumulative_PnL).map(date => ({
                    time: new Date(date).toISOString().split('T')[0],
                    value: data.Cumulative_PnL[date],
                }));
                areaSeries.setData(formattedData);
                chart.timeScale().fitContent();
            })
            .catch(error => console.error('Error fetching cumulative_PnL data:', error));

        chart.timeScale().fitContent();

        chart.applyOptions({
            layout: {
                padding: {
                    top: 0,
                    bottom: 0,
                    left: 0,
                    right: 0,
                },
            },
        });

        return () => {
            chart.remove();
        };
    }, []);

    return <div ref={chartContainerRef} style={{ width: '100%', height: '90%' }}></div>;
};

export default Chart;