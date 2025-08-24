import React from 'react';
import * as d3 from 'd3';
import * as crossfilter from 'crossfilter2/crossfilter';
import { ResponsiveBar } from '@nivo/bar';

const Bar = (props) => {
  const { x, y, margin, data, height, metric } = props;
  const cx = crossfilter(data);
  const dimension = cx.dimension((d) => d[x]);
  let group;
  if (metric === 'mean') {
    group = dimension.group().reduce(
      (p, v) => {
        ++p.count;
        p.sum += v[y];
        p.avg = p.sum / p.count;
        return p;
      },
      (p, v) => {
        --p.count;
        p.sum += v[y];
        p.avg = p.sum / p.count;
        return p;
      },
      () => ({
        count: 0,
        sum: 0,
        avg: 0,
      })
    );
  } else if (metric === 'median') {
    group = dimension.group().reduce(
      (p, v) => {
        p.values.push(v[y]);
        p.values.sort(d3.ascending);
        const middle = Math.floor(p.values.length / 2);
        p.median =
          p.values.length % 2 !== 0
            ? p.values[middle]
            : (p.values[middle - 1] + p.values[middle]) / 2;
        return p;
      },
      (p, v) => {
        p.values = p.values.filter((value) => value !== v[y]);
        p.values.sort(d3.ascending);
        const middle = Math.floor(p.values.length / 2);
        p.median =
          p.values.length % 2 !== 0
            ? p.values[middle]
            : (p.values[middle - 1] + p.values[middle]) / 2;
        return p;
      },
      () => ({
        values: [],
        median: 0,
      })
    );
  }

  const processedData = group
    .top(Infinity)
    .map((d) => {
      d.valueToShow = metric === 'mean' ? d.value.avg : d.value.median;
      d.valueToShow = Math.round(d.valueToShow * 1000) / 1000;
      // Change "Otro lenguaje de programación" to "Otro" for programming language bars
      if (
        x === 'main-programming-language' &&
        d.key === 'Otro lenguaje de programación'
      ) {
        d.key = 'Otro';
      }
      return d;
    })
    .filter(d => d.valueToShow && !isNaN(d.valueToShow) && d.valueToShow > 0)
    .sort((a, b) => d3.ascending(a.valueToShow, b.valueToShow));

  // Handle empty data case
  if (processedData.length === 0) {
    return <div style={{ height: height }}>No data available</div>;
  }

  const values = processedData.map(d => d.valueToShow).filter(v => v && !isNaN(v));
  const maxValue = Math.max(...values) || 1;
  const minValue = Math.min(...values) || 0;
  const range = maxValue - minValue || 1;

  return (
    <div style={{ height: height }}>
      <ResponsiveBar
        margin={margin}
        padding={0.2}
        data={processedData}
        indexBy="key"
        enableGridX={true}
        enableGridY={true}
        keys={['valueToShow']}
        colors={({ data }) => {
          const normalizedValue = Math.max(0, Math.min(1, (data.valueToShow - minValue) / range));
          const lightness = Math.max(40, Math.min(80, 80 - (normalizedValue * 40)));
          return `hsl(48, 100%, ${lightness}%)`;
        }}
        borderWidth={3}
        borderColor="#000"
        enableLabel={true}
        labelFormat={(v) => `${d3.format('($,.1f')(v)}`}
        labelSkipWidth={20}
        tooltipFormat={(v) => `${d3.format('($,.1f')(v)}`}
        isInteractive={true}
        animate={false}
        layout="horizontal"
        axisBottom={{
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          tickValues: 5,
        }}
      />
    </div>
  );
};
export default Bar;
