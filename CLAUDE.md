# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a React-based salary visualization application for Colombian developers using 2025 survey data. It processes CSV salary data and creates interactive charts filtered by developer profiles (experience, English level, education, etc.).

## Development Commands

- `npm start` - Start development server
- `npm run build` - Build for production 
- `npm test` - Run tests
- `npm run deploy` - Deploy to GitHub Pages (runs build first)

## Architecture

### Core Components
- **App.js**: Main application component handling data loading, filtering logic, and state management
- **components/slider/**: Interactive D3-based sliders for user input (experience, English level, education, exchange rate, prestacional factor)
- **components/bar/**: Horizontal bar charts using Nivo and Crossfilter for salary data visualization

### Data Processing
- Raw salary data loaded from `src/data/salaries-2025-processed.csv`
- Currency conversion applied (USD to COP using configurable exchange rate)
- Prestacional factor calculation for employees with "Laboral" contracts
- Multi-dimensional filtering by experience range, English level, and education level

### Key Libraries
- **D3.js**: Data processing, formatting, and slider interactions
- **Nivo**: Bar chart rendering
- **Crossfilter2**: Fast data filtering and aggregation
- **Material-UI**: UI components and layout
- **d3-simple-slider**: Interactive range sliders

### Data Flow
1. CSV data loaded and parsed in App.js `processData()`
2. Filters applied in `useEffect` hook trigger data recalculation
3. Filtered data passed to Bar components for visualization
4. Crossfilter dimensions and groups handle chart aggregations

### Deployment
- Configured for GitHub Pages deployment
- Homepage set to `https://jaimegarcia.github.io/colombia-salary-viz-2025`
- Uses `gh-pages` package for automated deployment