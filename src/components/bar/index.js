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
        p.median = p.values.length % 2 !== 0 ?
          p.values[middle] :
          (p.values[middle - 1] + p.values[middle]) / 2;
        return p;
      },
      (p, v) => {
        p.values = p.values.filter(value => value !== v[y]);
        p.values.sort(d3.ascending);
        const middle = Math.floor(p.values.length / 2);
        p.median = p.values.length % 2 !== 0 ?
          p.values[middle] :
          (p.values[middle - 1] + p.values[middle]) / 2;
        return p;
      },
      () => ({
        values: [],
        median: 0,
      })
    );
  }

  return (
    <div style={{ height: height }}>
      <ResponsiveBar
        margin={margin}
        padding={0.2}
data={group
          .top(Infinity)
          .map((d) => {
            d.valueToShow = metric === 'mean' ? d.value.avg : d.value.median;
            d.valueToShow = Math.round(d.valueToShow * 1000) / 1000;
            return d;
          })
          .sort((a, b) => d3.ascending(a.valueToShow, b.valueToShow))}
        indexBy="key"
        enableGridX={true}
        enableGridY={true}
keys={['valueToShow']}
        colors={['#F1E15B']}
        borderWidth={3}
        borderColor="#000"
        enableLabel={true}
        labelFormat={(v) => `${d3.format('($,.1f')(v)}`}
        labelSkipWidth={20}
        tooltipFormat={(v) => `${d3.format('($,.1f')(v)}`}
        isInteractive={true}
        animate={false}
        layout="horizontal"
      />
    </div>
  );
};
export default Bar;
