import { Component, Input, OnInit } from '@angular/core';
import { ChargingPlanElement, TimelineEntry } from '../../models/car.model';
import { CommonModule } from '@angular/common';
import { BaseChartDirective } from 'ng2-charts';
import { ChartOptions, ChartType, ChartDataset, ChartData } from 'chart.js';
import { de } from 'date-fns/locale';
import 'chartjs-adapter-date-fns';

@Component({
  selector: 'app-charging-timeline',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './charging-timeline.component.html',
  styleUrl: './charging-timeline.component.css'
})
export class ChargingTimelineComponent implements OnInit {
  @Input() timelineData: TimelineEntry[] = [];

  public lineChartOptions: ChartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      intersect: false,
      axis: 'x'
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'minute',
          displayFormats: {
            minute: 'HH:mm'
          }
        },
        ticks: {
          source: 'data',
          minRotation: 80,
        },
      },
      y: {
        title: {
          display: false,
        },
        display: false
      }
    },
    plugins: {
      tooltip: {
        enabled: false
      }
    }
  };

  public lineChartType: ChartType = 'line';
  public lineChartData: any

  constructor() { }

  ngOnInit() {
    this.updateChartData();
  }

  updateChartData(): void {
      const dataMap: Record<string, {x : Date, y: number}[]> = {
        'inUse': [],
        'charging': [],
        'idle': []
      };

      const typeToLabel: Record<string, string> = {
        'inUse': 'Booked',
        'charging': 'Charging',
        'idle': 'Idle'
      };
  
      // Populate chart data from timeline data
      this.timelineData.forEach(entry => {
        dataMap[entry.type].push({ x: new Date(entry.from), y: 1 }),
        dataMap[entry.type].push({ x: new Date(entry.to), y: 0 })
      });
  
      // Convert the dataMap into the chart data format
      this.lineChartData = Object.keys(dataMap).map(type => ({
        data: dataMap[type],
        label: typeToLabel[type],
        borderColor: this.getColor(type),
        backgroundColor: this.getColor(type),
        stepped: "before",
        fill: {
          target: "origin",
          above: this.getColor(type)
        },
        borderWidth: 0,
        pointRadius: 0,
      }));
    }
  
    private getColor(type: string): string {
      switch (type) {
        case 'inUse': return '#ff6384';
        case 'charging': return '#7cb05b';
        case 'idle': return '#919191';
        default: return '#cccccc';
      }
    }
}
