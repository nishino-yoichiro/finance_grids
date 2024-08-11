import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const Chart = ({ dataType }) => {
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

        let series;
        if (dataType === 'Cumulative_PnL') {
            series = chart.addBaselineSeries({
                baseValue: { type: 'price', price: 0 },
                topLineColor: 'rgba(38, 166, 154, 1)',
                topFillColor1: 'rgba(38, 166, 154, 0.28)',
                topFillColor2: 'rgba(38, 166, 154, 0.05)',
                bottomLineColor: 'rgba(239, 83, 80, 1)',
                bottomFillColor1: 'rgba(239, 83, 80, 0.05)',
                bottomFillColor2: 'rgba(239, 83, 80, 0.28)',
            });
        } else {
            series = chart.addHistogramSeries({ color: '#26a69a' });
        }

        const fileName = 'orders.csv';
        const url = `http://localhost:5000/api/pnl?file_name=${fileName}&type=${dataType}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const formattedData = Object.keys(data[dataType]).map(date => ({
                    time: new Date(date).toISOString().split('T')[0],
                    value: data[dataType][date],
                    color: data[dataType][date] >= 0 ? 'rgba(38, 166, 154, 1)' : 'rgba(239, 83, 80, 1)',
                }));
                series.setData(formattedData);
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