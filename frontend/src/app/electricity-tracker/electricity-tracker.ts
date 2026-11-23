
import {
  Component,
  OnInit,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import {
  ElectricityEntry,
  ElectricityService
} from '../services/electricity.service';

@Component({
  selector: 'app-electricity-tracker',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './electricity-tracker.html',
  styleUrl: './electricity-tracker.css'
})
export class ElectricityTracker implements OnInit {

  electricityEntries: ElectricityEntry[] = [];

  quantityKwh: number | null = null;
  activityDate = this.getTodayDate();

  isLoadingHistory = true;
  isSaving = false;

  deletingEntryId: string | null = null;

  errorMessage = '';
  historyErrorMessage = '';
  successMessage = '';

  savedEntry: ElectricityEntry | null = null;

  constructor(
    private electricityService: ElectricityService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadElectricityEntries();
  }

  private getTodayDate(): string {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  async loadElectricityEntries(): Promise<void> {
    this.isLoadingHistory = true;
    this.historyErrorMessage = '';

    try {
      this.electricityEntries =
        await this.electricityService.getElectricityEntries();

    } catch (error) {
      console.error(
        'Unable to load electricity history:',
        error
      );

      this.historyErrorMessage =
        'Unable to load your electricity history. Please try again.';

    } finally {
      this.isLoadingHistory = false;
      this.cdr.detectChanges();
    }
  }

  get totalElectricityKwh(): number {
    return this.electricityEntries.reduce(
      (total, entry) =>
        total + Number(entry.quantity_kwh || 0),
      0
    );
  }

  get totalElectricityEmissions(): number {
    return this.electricityEntries.reduce(
      (total, entry) =>
        total + Number(entry.emissions_kg_co2 || 0),
      0
    );
  }

  get totalEntries(): number {
    return this.electricityEntries.length;
  }

  async saveElectricityEntry(): Promise<void> {
    this.errorMessage = '';
    this.historyErrorMessage = '';
    this.successMessage = '';
    this.savedEntry = null;

    if (
      this.quantityKwh === null ||
      !Number.isFinite(this.quantityKwh) ||
      this.quantityKwh <= 0
    ) {
      this.errorMessage =
        'Please enter electricity consumption greater than zero kWh.';
      return;
    }

    if (!this.activityDate) {
      this.errorMessage =
        'Please select the electricity consumption date.';
      return;
    }

    this.isSaving = true;

    try {
      this.savedEntry =
        await this.electricityService.createElectricityEntry({
          quantity_kwh: this.quantityKwh,
          activity_date: this.activityDate
        });

      this.quantityKwh = null;

      await this.loadElectricityEntries();

      this.successMessage = this.historyErrorMessage
        ? 'Electricity entry saved, but history could not be refreshed.'
        : 'Electricity entry saved successfully.';

    } catch (error) {
      console.error(
        'Unable to save electricity entry:',
        error
      );

      this.errorMessage =
        'Unable to save your electricity entry. Please try again.';

    } finally {
      this.isSaving = false;
      this.cdr.detectChanges();
    }
  }

  async deleteElectricityEntry(
    entry: ElectricityEntry
  ): Promise<void> {
    const confirmed = window.confirm(
      `Are you sure you want to delete the ${entry.quantity_kwh} kWh electricity entry?`
    );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';
    this.historyErrorMessage = '';
    this.successMessage = '';

    this.deletingEntryId = entry.id;

    try {
      await this.electricityService.deleteElectricityEntry(
        entry.id
      );

      await this.loadElectricityEntries();

      this.successMessage = this.historyErrorMessage
        ? 'Electricity entry deleted, but history could not be refreshed.'
        : 'Electricity entry deleted successfully.';

    } catch (error) {
      console.error(
        'Unable to delete electricity entry:',
        error
      );

      this.errorMessage =
        'Unable to delete this electricity entry. Please try again.';

    } finally {
      this.deletingEntryId = null;
      this.cdr.detectChanges();
    }
  }
}
