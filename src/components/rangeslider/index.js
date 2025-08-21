import React, { useState, useEffect, useRef } from 'react';
import * as d3 from 'd3';
import * as d3Slider from 'd3-simple-slider';
import './styles.css';

const RangeSlider = (props) => {
  const {
    min,
    max,
    step,
    defaultMin,
    defaultMax,
    variable,
    ordinalScale,
    updateRangeChart,
  } = props;

  const ref = useRef(null);
  const [selectedRange, setSelectedRange] = useState([defaultMin, defaultMax]);

  useEffect(() => {
    const width = 320;
    const height = 80;
    const margin = { top: 20, right: 30, bottom: 60, left: 30 };

    const svg = d3
      .select(ref.current)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const xLinear = d3
      .scaleLinear()
      .domain([min, max])
      .range([margin.left, width - margin.right]);

    const slider = (g) =>
      g.attr('transform', `translate(0,${height - margin.bottom})`).call(
        d3Slider
          .sliderBottom(xLinear)
          .step(step)
          .ticks(4)
          .default([defaultMin, defaultMax])
          .fill('#2196F3')
          .on('onchange', (value) => draw(value))
      );

    svg.append('g').call(slider);

    const draw = (selected) => {
      setSelectedRange(selected);
      updateRangeChart(variable, selected[0], selected[1]);
    };

    draw([defaultMin, defaultMax]);
  }, []);

  const formatValue = (value) => {
    if (ordinalScale) {
      return ordinalScale[value] || value;
    }
    return value;
  };

  return (
    <React.Fragment>
      <p>
        {formatValue(selectedRange[0])} - {formatValue(selectedRange[1])}
      </p>
      <div id="range-slider" ref={ref}></div>
    </React.Fragment>
  );
};

export default RangeSlider;
