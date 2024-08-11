import React from 'react';
import './Box.css';
import Chart from './charts.js';
import MyCalendar from './Calendar.js';

function Box({ type, width, height, content }) {
    const value = parseFloat(content.value);
    const averageTrades = parseFloat(content.averageTrades);
    const valueClass = value < 0 ? 'negative' : 'positive';
    const averageTradesClass = averageTrades < 0 ? 'negative' : 'positive';

    return (
        <>
            <div className={`grid-item ${type}`} style={{ width, height }}>
                {type === 'box-net-profit-loss' && (
                    <>
                        <div className="label">{content.label}</div>
                            {content.variation === 'totalTrades' ? (
                                <>
                                    <div>
                                        <div className={`value ${valueClass}`}>${Math.abs(content.value)}</div>
                                    </div>
                                    <div>
                                        <div className="total-trades">Trades in total: {content.totalTrades}</div>
                                    </div>
                                </>
                            ) : (
                                <div className="top-row">
                                    <div className={`value ${valueClass}`}>${Math.abs(content.value)}</div>
                                    {content.variation === 'averageCons' && (
                                        <div className={`average-trades ${averageTradesClass}`}>{Math.abs(content.averageTrades)}</div>
                                    )}
                                </div>
                            )}
                    </>
                )}
                {type === 'Charts' && (
                    <div className="box-daily-pnl">
                        <div className="label">{content.label}</div>
                        <div className="chart-container">
                            <Chart dataType={content.dataType}/>
                        </div>
                    </div>
                )}
                {type === 'Calendar' && (
                    <div className="box-calendar">
                        <div className="calendar-container">
                            <MyCalendar />
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}

export default Box;