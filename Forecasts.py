import sys
import os
from datetime import datetime
import pandas
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates
import plot_helper

plt.ion()


class Forecasts(object):
    def __init__(self, location, forecasts_dir='Forecasts', history_dir='History', hourly=False):
        self.location = location
        self.hourly = hourly
        if hourly:
            forecasts_dir += '_hourly'
            history_dir += '_hourly'
        self.forecasts_dir = forecasts_dir
        self.history_dir = history_dir
        self.read_forecasts()
        self.read_history()

    def read_forecasts(self):
        self.forecast_list = []
        all_forecasts = os.listdir(self.forecasts_dir)
        for f in all_forecasts:
            if f.startswith(self.location):
                f_path = os.path.join(self.forecasts_dir, f)
                self.forecast_list.append(pandas.read_csv(f_path))

    def read_history(self):
        h_path = os.path.join(self.history_dir, self.location+'.csv')
        self.history = pandas.read_csv(h_path)

    def _get_dates_list(self, dates):
        if self.hourly:
            return dates # Alternate version
        else:
            if self.hourly:
                result = [datetime.strptime(d, "%m/%d/%Y %H:%M:%S").date() for d in dates]
            else:
                result = [datetime.strptime(d, "%m/%d/%Y").date() for d in dates]
            return result

    def plot_temperature_hi_lo(self):
        fig, ax = plt.subplots(figsize=(10., 8.))

        for forecast in self.forecast_list:
            #dates = forecast['Date time']
            dates = self._get_dates_list(forecast['Date time'])
            #ax.plot(dates, forecast['Maximum Temperature'], 'r')
            #ax.plot(dates, forecast['Minimum Temperature'], 'b')
            n = len(forecast['Maximum Temperature'])
            datenum = matplotlib.dates.date2num(dates)
            scale = n - np.arange(n-1)
            norm = plt.Normalize(-n//8, n)
            plot_helper.colored_line(ax, datenum, forecast['Maximum Temperature'], scale, norm=norm, cmap=plt.get_cmap('Reds'))
            plot_helper.colored_line(ax, datenum, forecast['Minimum Temperature'], scale, norm=norm, cmap=plt.get_cmap('Blues'))

        dates = self._get_dates_list(self.history['Date time'])
        ax.plot(dates, self.history['Maximum Temperature'], 'm', linewidth=2.5)
        ax.plot(dates, self.history['Minimum Temperature'], 'c', linewidth=2.5)

        ax.xaxis.set_major_locator(plt.MaxNLocator(25))
        ax.set_xlabel('Date')
        ax.set_ylabel('Temperature extremum')
        ax.set_title(f'All data for {self.location}')
        ax.tick_params(right=True, labelright=False, which='both')
        if self.hourly:
            fig.autofmt_xdate(matplotlib.dates.DateFormatter('%m/%d/%Y %H:%M:%S'))
        else:
            fig.autofmt_xdate()
        fig.show()

    def _plot_quantity(self, quantity):
        fig, ax = plt.subplots(figsize=(10., 8.))

        for forecast in self.forecast_list:
            dates = self._get_dates_list(forecast['Date time'])
            if self.hourly:
                ax.plot(dates, forecast[quantity], 'r')
            else:
                n = len(forecast[quantity])
                datenum = matplotlib.dates.date2num(dates)
                scale = n - np.arange(n-1)
                norm = plt.Normalize(-n//4, n)
                plot_helper.colored_line(ax, datenum, forecast[quantity], scale, norm=norm, cmap=plt.get_cmap('Reds'))

        dates = self._get_dates_list(self.history['Date time'])
        ax.plot(dates, self.history[quantity], 'm', linewidth=2.5)

        ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        ax.set_xlabel('Date')
        ax.set_ylabel(quantity)
        ax.set_title(f'All data for {self.location}')
        ax.tick_params(right=True, labelright=False, which='both')
        if self.hourly:
            fig.autofmt_xdate(matplotlib.dates.DateFormatter('%m/%d/%Y %H:%M:%S'))
        else:
            fig.autofmt_xdate()

        fig.show()

    def plot_precipitation(self): self._plot_quantity('Precipitation')
    def plot_humidity(self): self._plot_quantity('Relative Humidity')

    def plot_temperature_hourly(self): self._plot_quantity('Temperature')

    def _plot_relative(self, quantity):
        relative_days = []
        relative_records = []

        h_datenums = matplotlib.dates.date2num(self._get_dates_list(self.history['Date time']))
        for h_date, h_datenum, h_record in zip(self.history['Date time'], h_datenums, self.history[quantity]):
            for forecast in self.forecast_list:
                forecast_record = forecast[forecast['Date time'] == h_date][quantity]
                if len(forecast_record) > 0:
                    forecast_datenums = matplotlib.dates.date2num(self._get_dates_list(forecast['Date time']))
                    forecast_datenum = forecast_datenums[0]
                    relative_days.append(forecast_datenum - h_datenum)
                    relative_records.append(forecast_record.values[0] - h_record)

        fig, ax = plt.subplots(figsize=(10., 8.))
        ax.plot(relative_days, relative_records, linestyle='', marker='o')
        ax.set_xlabel('Days before actual')
        ax.set_ylabel(f'Relative {quantity}')
        ax.tick_params(right=True, labelright=False, which='both')
        ax.set_title(f'All data for {self.location}')
        fig.show()

    def _plot_relative_histogram(self, quantity, npoints=20):
        h_datenums = matplotlib.dates.date2num(self._get_dates_list(self.history['Date time']))

        rmin = 0.
        rmax = 0.
        for h_date, h_datenum, h_record in zip(self.history['Date time'], h_datenums, self.history[quantity]):
            for forecast in self.forecast_list:
                forecast_record = forecast[forecast['Date time'] == h_date][quantity]
                if len(forecast_record) > 0:
                    r = forecast_record.values[0] - h_record
                    rmin = min(rmin, r)
                    rmax = max(rmax, r)

        ndays = 14
        relative_histograms = np.zeros((npoints, ndays+1))

        rmax += (rmax - rmin)/1000. # make sure that max r < rmax
        dr = (rmax - rmin)/npoints

        for h_date, h_datenum, h_record in zip(self.history['Date time'], h_datenums, self.history[quantity]):
            for forecast in self.forecast_list:
                forecast_record = forecast[forecast['Date time'] == h_date][quantity]
                if len(forecast_record) > 0:
                    forecast_datenums = matplotlib.dates.date2num(self._get_dates_list(forecast['Date time']))
                    forecast_datenum = forecast_datenums[0]
                    idays = int(h_datenum - forecast_datenum + 0.5)
                    if idays > ndays:
                        continue
                    r = forecast_record.values[0] - h_record
                    ir = int((r - rmin)/dr)
                    relative_histograms[ir,idays] += 1.

        fig, ax = plt.subplots(figsize=(10., 8.))
        im = ax.imshow(relative_histograms[:,::-1], aspect='auto', origin='lower', extent=(-ndays-0.5, 0.5, rmin, rmax))
        fig.colorbar(im, ax=ax)
        ax.set_xlabel('Days before actual')
        ax.set_ylabel(f'Relative {quantity}')
        ax.tick_params(right=True, labelright=False, which='both')
        ax.set_title(f'All data for {self.location}')
        fig.show()

    def plot_relative_min_temp(self): self._plot_relative('Minimum Temperature')
    def plot_relative_max_temp(self): self._plot_relative('Maximum Temperature')
    def plot_relative_precipitation(self): self._plot_relative('Precipitation')
    def plot_relative_humidity(self): self._plot_relative('Relative Humidity')
    def plot_relative_min_temp_histogram(self): self._plot_relative_histogram('Minimum Temperature')
    def plot_relative_max_temp_histogram(self): self._plot_relative_histogram('Maximum Temperature')
    def plot_relative_precipitation_histogram(self): self._plot_relative_histogram('Precipitation')
    def plot_relative_humidity_histogram(self): self._plot_relative_histogram('Relative Humidity')

if __name__ == '__main__':

    if len(sys.argv) > 1:
        city = sys.argv[1]
    else:
        city = 'Orinda'
    if len(sys.argv) > 2:
        aggregateHours = sys.argv[2]
    else:
        aggregateHours = '24'
    hourly = (aggregateHours=='1')

    forecasts = Forecasts(city, hourly=hourly)
    if hourly:
        forecasts.plot_temperature_hourly()
    else:
        forecasts.plot_humidity()
        forecasts.plot_precipitation()
        forecasts.plot_relative_max_temp_histogram()
        forecasts.plot_relative_max_temp()
        forecasts.plot_temperature_hi_lo()

