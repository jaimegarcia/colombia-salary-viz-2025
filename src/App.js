import React, { useState, useEffect } from 'react';
import Slider from './components/slider';
import RangeSlider from './components/rangeslider';
import Bar from './components/bar';
import {
  Box,
  Grid,
  AppBar,
  Toolbar,
  Typography,
  Button,
  ButtonGroup,
  Paper,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import * as d3 from 'd3';

import './App.css';
import salaryFile from './data/salaries-2025-processed.csv';
//let salaryData=null;

const maxSalary = 1000000000;
const englishLevels = ['Ninguno', 'Básico', 'Intermedio', 'Avanzado', 'Nativo'];
const educationTitles = [
  '', // placeholder for index 0
  'Ninguna',
  'Bachiller',
  'Técnica',
  'Tecnóloga/o',
  'Pregrado',
  'Posgrado',
];
function App() {
  const [loading, setLoading] = useState(true);
  const [salaryMean, setSalaryMean] = useState(0);
  const [salaryMedian, setSalaryMedian] = useState(0);
  const [showMedian, setShowMedian] = useState(false);
  const [displayCurrency, setDisplayCurrency] = useState('COP'); // Add currency state
  const [numberOfPeople, setNumberOfPeople] = useState(0);
  const [salaryData, setSalaryData] = useState(null);
  const [filteredData, setFilteredData] = useState(null);
  const [filters, setFilters] = React.useState({
    exchangeRate: 4300,
    experience: { min: 0, max: 15 }, // Changed to range
    'english-level': { min: 0, max: 4 }, // Changed to range
    'max-title': { min: 0, max: 7 }, // Changed to range
    'factor-prestacional': 0.35, // Default 35% factor
  });
  const [contractTypeFilters, setContractTypeFilters] = React.useState({
    Laboral: true,
    'Prestación de servicios/Contractor/Independiente': true,
  });
  const processData = () => {
    d3.csv(salaryFile, (d) => {
      return {
        currency: d['currency'],
        'main-programming-language': d['main-programming-language'],
        'company-type': d['company-type'].replace('empresa', ''),
        position: d['position'],
        workmode: d['workmode'],
        'contract-type': d['contract-type'],
        'min-experience': +d['min-experience'],
        'max-experience': +d['max-experience'],
        'english-level': +d['english-level'],
        'max-title': +d['max-title'],
        'income-in-currency': +d['income-in-currency'],
      };
    })
      .then((csv) => {
        console.log(csv);
        setSalaryData(csv);
        setLoading(false);
      })
      .catch((error) => {
        // handle error
      });
  };

  const updateChart = (name, value) => {
    setFilters((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const updateRangeChart = (name, min, max) => {
    setFilters((prevState) => ({
      ...prevState,
      [name]: { min, max },
    }));
  };

  const toggleContractType = (contractType) => {
    setContractTypeFilters((prevState) => ({
      ...prevState,
      [contractType]: !prevState[contractType],
    }));
  };

  const getCurrencyLabel = () => {
    return displayCurrency === 'USD' ? 'USD al año' : 'Millones de pesos al año';
  };

  useEffect(() => {
    processData(setSalaryData, setLoading);
  }, []);

  useEffect(() => {
    if (salaryData) {
      let newSalaryData = salaryData.map((d) => {
        let baseSalary =
          d['currency'] === 'Pesos'
            ? d['income-in-currency'] / 1e6
            : (d['income-in-currency'] * filters.exchangeRate) / 1e6;

        // Apply prestacional factor ONLY for people with Laboral contract
        if (d['contract-type'] === 'Laboral') {
          baseSalary = baseSalary * (1 + filters['factor-prestacional']);
        }

        d['income-cop'] = baseSalary;
        return d;
      });

      newSalaryData = newSalaryData.filter(
        (d) =>
          d['income-cop'] <= maxSalary &&
          d['min-experience'] <=
            (filters.experience.max >= 15
              ? Infinity
              : filters.experience.max) &&
          d['max-experience'] >= filters.experience.min &&
          d['english-level'] >= filters['english-level'].min &&
          d['english-level'] <= filters['english-level'].max &&
          d['max-title'] >= filters['max-title'].min &&
          d['max-title'] <= filters['max-title'].max &&
          contractTypeFilters[d['contract-type']]
      );

      setFilteredData(newSalaryData);
      setSalaryMean(
        Math.round(d3.mean(newSalaryData, (d) => d['income-cop']) * 1000) / 1000
      );
      setSalaryMedian(
        Math.round(d3.median(newSalaryData, (d) => d['income-cop']) * 1000) /
          1000
      );
      setNumberOfPeople(newSalaryData.length);
    }
  }, [filters, contractTypeFilters, salaryData]);

  return (
    <div className="App">
      <AppBar position="static">
        <Toolbar>
          <Typography className="title" variant="h6">
            Visualización de Salarios de Desarrolladores Colombianos 2025
          </Typography>
        </Toolbar>
      </AppBar>
      <h3>
        Hecho por Jaime García. Datos: Encuesta de La Plaza Devs 2025 (931
        personas)
      </h3>

      {!loading && (
        <Box style={{ padding: 16 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <b>¿Qué tasa de conversión de dólar deseas utilizar?</b>
              <Slider
                variable="exchangeRate"
                updateChart={updateChart}
                min={3500}
                defaultValue={4000}
                max={4500}
                step={10}
              />
              <b>Factor Prestacional para empleados con contrato laboral (%)</b>
              <Slider
                variable="factor-prestacional"
                updateChart={updateChart}
                min={0}
                defaultValue={0.45}
                max={1.0}
                step={0.05}
              />
              <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                Porcentaje adicional aplicado al salario de empleados con
                contrato laboral para incluir prestaciones sociales (cesantías,
                prima, vacaciones, etc.)
              </p>
              <b>¿Cuántos años de experiencia tienes?</b>
              <RangeSlider
                variable="experience"
                updateRangeChart={updateRangeChart}
                min={0}
                defaultMin={0}
                defaultMax={15}
                max={15}
                step={1}
              />
              <b>¿Cuál es tu nivel de ingles?</b>
              <RangeSlider
                variable="english-level"
                updateRangeChart={updateRangeChart}
                min={0}
                defaultMin={0}
                defaultMax={4}
                max={4}
                step={1}
                ordinalScale={englishLevels}
              />
              <b>¿Cuál es tu máximo nivel de formación?</b>
              <RangeSlider
                variable="max-title"
                updateRangeChart={updateRangeChart}
                min={1}
                defaultMin={1}
                defaultMax={6}
                max={6}
                step={1}
                ordinalScale={educationTitles}
              />
            </Grid>
            <Grid item xs={12} md={8}>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Box sx={{ mb: 2 }}>
                    <ToggleButtonGroup
                      value={showMedian ? 'median' : 'mean'}
                      exclusive
                      onChange={(event, newValue) => {
                        if (newValue !== null) {
                          setShowMedian(newValue === 'median');
                        }
                      }}
                      aria-label="metric selection"
                      sx={{ mr: 2 }}
                    >
                      <ToggleButton value="mean" aria-label="mean">
                        Promedio
                      </ToggleButton>
                      <ToggleButton value="median" aria-label="median">
                        Mediana
                      </ToggleButton>
                    </ToggleButtonGroup>
                    <ToggleButtonGroup
                      value={displayCurrency}
                      exclusive
                      onChange={(event, newValue) => {
                        if (newValue !== null) {
                          setDisplayCurrency(newValue);
                        }
                      }}
                      aria-label="currency selection"
                    >
                      <ToggleButton value="COP" aria-label="cop">
                        COP
                      </ToggleButton>
                      <ToggleButton value="USD" aria-label="usd">
                        USD
                      </ToggleButton>
                    </ToggleButtonGroup>
                  </Box>
                  <b>
                    <span>
                      Hay {numberOfPeople} persona
                      {numberOfPeople !== 1 && <span>s</span>} de la comunidad
                      con un perfil parecido al tuyo
                    </span>
                    {numberOfPeople > 0 && (
                      <span>
                        {' '}
                        y ganan en {showMedian ? 'mediana' : 'promedio'} el
                        equivalente a
                      </span>
                    )}
                  </b>
                  <h2>
                    {numberOfPeople > 0 && (
                      <React.Fragment>
                        <span>
                          {' '}
                          <h2>
                            <span className="salary-value">
                              {displayCurrency === 'USD' ? (
                                <>
                                  {d3.format('($,.0f')(
                                    ((showMedian ? salaryMedian : salaryMean) * 1000000) / filters.exchangeRate
                                  )}{' '}
                                  USD al año
                                </>
                              ) : (
                                <>
                                  {d3.format('($,.1f')(
                                    showMedian ? salaryMedian : salaryMean
                                  )}{' '}
                                  Millones de pesos al año
                                </>
                              )}
                            </span>
                          </h2>
                        </span>
                        <span className="salary-value">
                          {' '}
                          <span>
                            {displayCurrency === 'USD' ? (
                              <>
                                {d3.format('($,.0f')(
                                  ((showMedian ? salaryMedian : salaryMean) * 1000000) / filters.exchangeRate / 12
                                )}{' '}
                                USD
                              </>
                            ) : (
                              <>
                                {d3.format('($,.1f')(
                                  (showMedian ? salaryMedian : salaryMean) / 12
                                )}{' '}
                                Millones
                              </>
                            )}
                          </span>{' '}
                          {displayCurrency === 'USD' ? 'mensuales' : 'de pesos mensuales'}
                        </span>
                      </React.Fragment>
                    )}
                  </h2>
                </Grid>
                {numberOfPeople > 0 && filteredData && (
                  <Grid item xs={12} md={6}>
                    <b>
                      {showMedian ? 'Medianas' : 'Promedios'} por Lenguaje de
                      Programación ({getCurrencyLabel()})
                    </b>
                    <Bar
                      x="main-programming-language"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 100 }}
                      height={550}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
                      displayCurrency={displayCurrency}
                      exchangeRate={filters.exchangeRate}
                    />
                  </Grid>
                )}

                {numberOfPeople > 0 && filteredData && (
                  <Grid item xs={12} md={6}>
                    <b>
                      {showMedian ? 'Medianas' : 'Promedios'} por Tipo de
                      Empresa ({getCurrencyLabel()})
                    </b>
                    <Bar
                      x="company-type"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 220 }}
                      height={225}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
                      displayCurrency={displayCurrency}
                      exchangeRate={filters.exchangeRate}
                    />
                    <b>
                      {showMedian ? 'Medianas' : 'Promedios'} por Modo de
                      Trabajo ({getCurrencyLabel()})
                    </b>
                    <Bar
                      x="workmode"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 100 }}
                      height={325}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
                      displayCurrency={displayCurrency}
                      exchangeRate={filters.exchangeRate}
                    />
                  </Grid>
                )}
              </Grid>
            </Grid>
          </Grid>
        </Box>
      )}
    </div>
  );
}

export default App;
