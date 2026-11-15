
import {
  Component,
  OnInit,
  AfterViewInit,
  OnDestroy,
  ChangeDetectorRef,
  ElementRef,
  ViewChild
} from '@angular/core';
import { RouterLink } from '@angular/router';
import { DecimalPipe } from '@angular/common';
import { Activity, ActivityService } from '../services/activity';
import {
  Chart,
  ChartConfiguration,
  registerables
} from 'chart.js';

Chart.register(...registerables);

interface DailyEmissionSummary {
  label: string;
  date: string;
  co2: number;
  co2e: number;
  hasCo2Data: boolean;
  hasCo2eData: boolean;
  activityCount: number;
}

type ChartChoice =
  | 'bar'
  | 'line'
  | 'pie'
  | 'doughnut'
  | 'area'
  | 'horizontalBar'
  | 'stackedBar';

@Component({
  selector: 'app-weekly-summary',
  standalone: true,
  imports: [RouterLink, DecimalPipe],
  templateUrl: './weekly-summary.html',
  styleUrl: './weekly-summary.css'
})
export class WeeklySummary implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('weeklyChart')
  weeklyChartCanvas?: ElementRef<HTMLCanvasElement>;

  activities: Activity[] = [];
  isLoading = false;
  errorMessage = '';

  selectedChart: ChartChoice = 'bar';
  selectedEmissionMetric: 'co2' | 'co2e' = 'co2';

  showChartEmptyState = false;

  private chart?: Chart;
  private viewReady = false;

  readonly chartOptions: { label: string; value: ChartChoice }[] = [
    { label: 'Bar Chart', value: 'bar' },
    { label: 'Line Chart', value: 'line' },
    { label: 'Pie Chart', value: 'pie' },
    { label: 'Doughnut Chart', value: 'doughnut' },
    { label: 'Area Chart', value: 'area' },
    { label: 'Horizontal Bar Chart', value: 'horizontalBar' },
    { label: 'Stacked Bar Chart', value: 'stackedBar' }
  ];

  readonly weekDays = [
    'Monday',
    'Tuesday',
    'Wednesday',
    'Thursday',
    'Friday',
    'Saturday',
    'Sunday'
  ];

  constructor(
    private activityService: ActivityService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadActivities();
  }

  ngAfterViewInit(): void {
    this.viewReady = true;
    this.renderChart();
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  async loadActivities(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    this.chart?.destroy();
    this.chart = undefined;

    try {
      this.activities = await this.activityService.getActivities();
    } catch (error) {
      console.error('Unable to load weekly activities:', error);
      this.errorMessage =
        'Unable to load your activities. Please try again.';
    } finally {
      this.isLoading = false;
      this.cdr.detectChanges();
      this.renderChart();
    }
  }

  onChartChange(value: string): void {
    this.selectedChart = value as ChartChoice;
    this.renderChart();
  }

  onEmissionMetricChange(value: string): void {
    if (value !== 'co2' && value !== 'co2e') {
      return;
    }

    this.selectedEmissionMetric = value;
    this.renderChart();
  }

  private normaliseDate(date: string): string {
    return String(date ?? '').trim().slice(0, 10);
  }

  private formatDate(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  private get startOfWeek(): Date {
    const today = new Date();

    const start = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
    );

    const day = (start.getDay() + 6) % 7;
    start.setDate(start.getDate() - day);

    return start;
  }

  get weeklyActivities(): Activity[] {
    const start = this.formatDate(this.startOfWeek);

    const endDate = new Date(this.startOfWeek);
    endDate.setDate(endDate.getDate() + 7);

    const end = this.formatDate(endDate);

    return this.activities.filter(activity => {
      const date = this.normaliseDate(activity.date);
      return date >= start && date < end;
    });
  }

  get weeklyActivityCount(): number {
    return this.weeklyActivities.length;
  }

  get activitiesWithUnavailableEmissions(): number {
    return this.weeklyActivities.filter(activity =>
      activity.emissionsKgCo2 === null &&
      activity.emissionsKgCo2e === null
    ).length;
  }

  get totalWeeklyCo2(): number | null {
    const recorded = this.weeklyActivities.filter(
      activity => activity.emissionsKgCo2 !== null
    );

    if (recorded.length === 0) {
      return null;
    }

    return recorded.reduce(
      (total, activity) => total + activity.emissionsKgCo2!,
      0
    );
  }

  get totalWeeklyCo2e(): number | null {
    const recorded = this.weeklyActivities.filter(
      activity => activity.emissionsKgCo2e !== null
    );

    if (recorded.length === 0) {
      return null;
    }

    return recorded.reduce(
      (total, activity) => total + activity.emissionsKgCo2e!,
      0
    );
  }

  get averageDailyCo2(): number | null {
    return this.totalWeeklyCo2 === null
      ? null
      : this.totalWeeklyCo2 / 7;
  }

  get averageDailyCo2e(): number | null {
    return this.totalWeeklyCo2e === null
      ? null
      : this.totalWeeklyCo2e / 7;
  }

  get dailyEmissions(): DailyEmissionSummary[] {
    const start = this.startOfWeek;

    return this.weekDays.map((label, index) => {
      const date = new Date(start);
      date.setDate(start.getDate() + index);

      const dateString = this.formatDate(date);

      const dayActivities = this.weeklyActivities.filter(
        activity =>
          this.normaliseDate(activity.date) === dateString
      );

      const co2Activities = dayActivities.filter(
        activity => activity.emissionsKgCo2 !== null
      );

      const co2eActivities = dayActivities.filter(
        activity => activity.emissionsKgCo2e !== null
      );

      return {
        label,
        date: dateString,
        co2: co2Activities.reduce(
          (total, activity) => total + activity.emissionsKgCo2!,
          0
        ),
        co2e: co2eActivities.reduce(
          (total, activity) => total + activity.emissionsKgCo2e!,
          0
        ),
        hasCo2Data: co2Activities.length > 0,
        hasCo2eData: co2eActivities.length > 0,
        activityCount: dayActivities.length
      };
    });
  }

  private renderChart(): void {
    if (
      !this.viewReady ||
      !this.weeklyChartCanvas ||
      this.isLoading ||
      this.errorMessage
    ) {
      return;
    }

    this.chart?.destroy();
    this.chart = undefined;
    this.showChartEmptyState = false;

    const canvas = this.weeklyChartCanvas.nativeElement;
    const context = canvas.getContext('2d');

    if (!context) {
      return;
    }

    const daily = this.dailyEmissions;
    const labels = daily.map(day => day.label);

    const co2Data = daily.map(day =>
      day.hasCo2Data ? day.co2 : null
    );

    const co2eData = daily.map(day =>
      day.hasCo2eData ? day.co2e : null
    );

    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'bottom' as const
        }
      }
    };

    let config: ChartConfiguration;

    switch (this.selectedChart) {
      case 'pie':
      case 'doughnut': {
        const categories = new Map<string, number>();

        this.weeklyActivities.forEach(activity => {
          const emissions = this.selectedEmissionMetric === 'co2'
            ? activity.emissionsKgCo2
            : activity.emissionsKgCo2e;

          if (emissions !== null) {
            const category = activity.type || 'Other';

            categories.set(
              category,
              (categories.get(category) ?? 0) + emissions
            );
          }
        });

        const hasPositiveEmissions = Array.from(categories.values())
          .some(value => value > 0);

        if (!hasPositiveEmissions) {
          this.showChartEmptyState = true;
          return;
        }

        config = {
          type: this.selectedChart,
          data: {
            labels: Array.from(categories.keys()),
            datasets: [{
              label: this.selectedEmissionMetric === 'co2'
                ? 'CO₂ (kg)'
                : 'CO₂e (kg)',
              data: Array.from(categories.values()),
              backgroundColor: [
                '#198754', '#73b98a', '#a5d6a7',
                '#4caf50', '#81c784', '#c8e6c9'
              ],
              borderWidth: 1
            }]
          },
          options: {
            ...baseOptions,
            plugins: {
              ...baseOptions.plugins,
              legend: {
                display: true,
                position: 'right'
              }
            }
          }
        };
        break;
      }

      case 'horizontalBar':
      case 'stackedBar': {
        config = {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'CO₂ (kg)',
                data: co2Data,
                backgroundColor: '#198754'
              },
              {
                label: 'CO₂e (kg)',
                data: co2eData,
                backgroundColor: '#a5d6a7'
              }
            ]
          },
          options: {
            ...baseOptions,
            indexAxis: this.selectedChart === 'horizontalBar' ? 'y' : 'x',
            scales: {
              x: {
                stacked: this.selectedChart === 'stackedBar'
              },
              y: {
                stacked: this.selectedChart === 'stackedBar',
                beginAtZero: true
              }
            }
          }
        };
        break;
      }

      case 'line':
      case 'area': {
        config = {
          type: 'line',
          data: {
            labels,
            datasets: [
              {
                label: 'CO₂ (kg)',
                data: co2Data,
                borderColor: '#198754',
                backgroundColor: 'rgba(25, 135, 84, 0.18)',
                fill: this.selectedChart === 'area',
                tension: 0.3,
                spanGaps: false
              },
              {
                label: 'CO₂e (kg)',
                data: co2eData,
                borderColor: '#8bcf9d',
                backgroundColor: 'rgba(139, 207, 157, 0.18)',
                fill: this.selectedChart === 'area',
                tension: 0.3,
                spanGaps: false
              }
            ]
          },
          options: {
            ...baseOptions,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        };
        break;
      }

      default: {
        config = {
          type: 'bar',
          data: {
            labels,
            datasets: [
              {
                label: 'CO₂ (kg)',
                data: co2Data,
                backgroundColor: '#198754'
              },
              {
                label: 'CO₂e (kg)',
                data: co2eData,
                backgroundColor: '#a5d6a7'
              }
            ]
          },
          options: {
            ...baseOptions,
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        };
      }
    }

    this.chart = new Chart(context, config);
  }
}
