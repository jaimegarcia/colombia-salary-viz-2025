import React, { useState, useEffect } from 'react';
import Slider from './components/slider';
import Bar from './components/bar';
import { Box, Grid, AppBar, Toolbar, Typography, Button, ButtonGroup, Paper, ToggleButton, ToggleButtonGroup } from '@mui/material';
import * as d3 from 'd3';

import './App.css';
import salaryFile from './data/salaries-2025-processed.csv';
//let salaryData=null;

const maxSalary = 1000000000;
const englishLevels = ['Ninguno', 'Básico', 'Intermedio', 'Avanzado', 'Nativo'];
const educationTitles = [
  'Ninguno',
  'Bachiller',
  'Técnico',
  'Tecnólogo',
  'Pregrado',
  'Especialista',
  'Maestría',
  'Doctorado',
];
function App() {
  const [loading, setLoading] = useState(true);
  const [salaryMean, setSalaryMean] = useState(0);
  const [salaryMedian, setSalaryMedian] = useState(0);
  const [showMedian, setShowMedian] = useState(false);
  const [numberOfPeople, setNumberOfPeople] = useState(0);
  const [salaryData, setSalaryData] = useState(null);
  const [filteredData, setFilteredData] = useState(null);
  const [filters, setFilters] = React.useState({
    exchangeRate: 4300,
    experience: 0,
    'english-level': 1,
    'max-title': 1,
    'factor-prestacional': 0.35, // Default 35% factor
  });
  const [contractTypeFilters, setContractTypeFilters] = React.useState({
    'Laboral': true,
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

  const toggleContractType = (contractType) => {
    setContractTypeFilters((prevState) => ({
      ...prevState,
      [contractType]: !prevState[contractType],
    }));
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
          filters.experience >= d['min-experience'] &&
          filters.experience <= d['max-experience'] &&
          filters['english-level'] === d['english-level'] &&
          filters['max-title'] === d['max-title'] &&
          contractTypeFilters[d['contract-type']]
      );

      setFilteredData(newSalaryData);
      setSalaryMean(
        Math.round(d3.mean(newSalaryData, (d) => d['income-cop']) * 1000) / 1000
      );
      setSalaryMedian(
        Math.round(d3.median(newSalaryData, (d) => d['income-cop']) * 1000) / 1000
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
                min={4000}
                defaultValue={4300}
                max={4500}
                step={10}
              />
              <b>Factor Prestacional para empleados con contrato laboral (%)</b>
              <Slider
                variable="factor-prestacional"
                updateChart={updateChart}
                min={0}
                defaultValue={0.3}
                max={1.0}
                step={0.05}
              />
              <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                Porcentaje adicional aplicado al salario de empleados con
                contrato laboral para incluir prestaciones sociales (cesantías,
                prima, vacaciones, etc.)
              </p>
              <b>¿Cuántos años de experiencia tienes?</b>
              <Slider
                variable="experience"
                updateChart={updateChart}
                min={0}
                defaultValue={5}
                max={15}
                step={1}
              />
              <b>¿Cuál es tu nivel de ingles?</b>
              <Slider
                variable="english-level"
                updateChart={updateChart}
                min={0}
                defaultValue={2}
                max={4}
                step={1}
                ordinalScale={englishLevels}
              />
              <b>¿Cuál es tu máximo nivel de formación?</b>
              <Slider
                variable="max-title"
                updateChart={updateChart}
                min={0}
                defaultValue={4}
                max={7}
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
                    >
                      <ToggleButton value="mean" aria-label="mean">
                        Promedio
                      </ToggleButton>
                      <ToggleButton value="median" aria-label="median">
                        Mediana
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
                      <span> y ganan en {showMedian ? 'mediana' : 'promedio'} el equivalente a</span>
                    )}
                  </b>
                  <h2>
                    {numberOfPeople > 0 && (
                      <React.Fragment>
                        <span>
                          {' '}
                          <h2>
                            <span className="salary-value">
                              {d3.format('($,.1f')(showMedian ? salaryMedian : salaryMean)} Millones de
                              pesos al año
                            </span>
                          </h2>
                        </span>
                        <span className="salary-value">
                          {' '}
                          <span>
                            {d3.format('($,.1f')((showMedian ? salaryMedian : salaryMean) / 12)} Millones
                          </span>{' '}
                          de pesos mensuales
                        </span>
                      </React.Fragment>
                    )}
                  </h2>
                </Grid>
                {numberOfPeople > 0 && filteredData && (
                  <Grid item xs={12} md={6}>
                    <b>
                      {showMedian ? 'Medianas' : 'Promedios'} por Lenguaje de Programación (Millones de pesos)
                    </b>
                    <Bar
                      x="main-programming-language"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 100 }}
                      height={550}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
                    />
                  </Grid>
                )}

                {numberOfPeople > 0 && filteredData && (
                  <Grid item xs={12} md={6}>
                    <b>{showMedian ? 'Medianas' : 'Promedios'} por Tipo de Empresa (Millones de pesos)</b>
                    <Bar
                      x="company-type"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 220 }}
                      height={225}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
                    />
                    <b>{showMedian ? 'Medianas' : 'Promedios'} por Modo de Trabajo (Millones de pesos)</b>
                    <Bar
                      x="workmode"
                      y="income-cop"
                      margin={{ top: 1.5, right: 50, bottom: 50, left: 100 }}
                      height={325}
                      data={filteredData}
                      metric={showMedian ? 'median' : 'mean'}
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
