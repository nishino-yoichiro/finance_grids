import React, { useState, useEffect} from 'react';
import { Calendar, momentLocalizer, Views} from 'react-big-calendar';
import moment from 'moment';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import './Calendar.css';

const CustomToolbar = (toolbar) => {
    const goToBack = () => {
        toolbar.onNavigate('PREV');
    };

    const goToNext = () => {
        toolbar.onNavigate('NEXT');
    };

    const goToCurrent = () => {
        toolbar.onNavigate('TODAY');
    };

    return (
        <div className="custom-toolbar">
            <div className="toolbar-left">
                <span>{toolbar.label}</span>
            </div>
            <div className="toolbar-right">
                <button onClick={goToBack}> &lt; </button>
                <button onClick={goToCurrent}>Today</button>
                <button onClick={goToNext}> &gt; </button>
            </div>
        </div>
    );
};

const localizer = momentLocalizer(moment);

const MyCalendar = () => {
    const [events] = useState([]);
    const [pnlData, setPnlData] = useState({});

    useEffect(() => {
        const fileName = 'orders.csv';
        fetch(`http://localhost:5000/api/pnl?file_name=${fileName}`)
            .then(response => response.json())
            .then(data => setPnlData(data.PnL_By_Day))
            .catch(error => console.error('Error fetching PnL data:', error));
    }, []);

    const profitColorProp = (date) => {
        const dateString = moment(date).format('MM/DD/YYYY');
        const pnl = pnlData[dateString] || 0;

        let backgroundColor;
        if (pnl > 0) {
            backgroundColor = '#59C0A4';
        } else if (pnl < 0) {
            backgroundColor = '#F6BFBE';
        }   else {
            backgroundColor = 'transparent';
        }

        return {
            className: 'day-cell',
            style: {
                backgroundColor,
                position: 'relative',
            },
            'data-pnl': pnl !== 0 ? pnl : '',
        };
    };

    const calendarStyle = {
        color: 'white',
        borderColor: 'white',
        fontWeight: 'bold',
    };

    return (
        <div style={{width:'100%', height:'100%'}}>
            <Calendar
                localizer={localizer}
                events={events}
                startAccessor="start"
                endAccessor="end"
                views={['month']}
                defaultView={Views.MONTH}
                style={{ height: '100%', width: '100%', ...calendarStyle}}
                components={{
                    toolbar: CustomToolbar,
                }}
                className="custom-calendar"
                dayPropGetter={profitColorProp}
            />
        </div>
    );
};

export default MyCalendar;