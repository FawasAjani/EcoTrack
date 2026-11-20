
import {
  Component,
  OnInit,
  ChangeDetectorRef
} from '@angular/core';

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';

import {
  FoodItem,
  FoodEntry,
  FoodService
} from '../services/food.service';

@Component({
  selector: 'app-food-tracker',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterLink
  ],
  templateUrl: './food-tracker.html',
  styleUrl: './food-tracker.css'
})
export class FoodTracker implements OnInit {

  foodItems: FoodItem[] = [];
  foodEntries: FoodEntry[] = [];

  selectedFoodId = '';
  quantityGrams: number | null = null;
  activityDate = this.getTodayDate();

  isLoading = true;
  isLoadingHistory = true;
  isSaving = false;

  deletingEntryId: string | null = null;

  errorMessage = '';
  historyErrorMessage = '';
  successMessage = '';

  savedEntry: FoodEntry | null = null;

  constructor(
    private foodService: FoodService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await Promise.all([
      this.loadFoodItems(),
      this.loadFoodEntries()
    ]);
  }

  private getTodayDate(): string {
    const today = new Date();

    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');

    return `${year}-${month}-${day}`;
  }

  async loadFoodItems(): Promise<void> {
    this.isLoading = true;
    this.errorMessage = '';

    try {
      this.foodItems = await this.foodService.getFoodItems();

      console.log(
        'Food catalogue loaded:',
        this.foodItems.length
      );

    } catch (error) {
      console.error(
        'Unable to load food catalogue:',
        error
      );

      this.errorMessage =
        'Unable to load the food catalogue. Please try again.';

    } finally {
      this.isLoading = false;
      this.cdr.detectChanges();
    }
  }

  async loadFoodEntries(): Promise<void> {
    this.isLoadingHistory = true;
    this.historyErrorMessage = '';

    try {
      this.foodEntries = await this.foodService.getFoodEntries();

      console.log(
        'Food history loaded:',
        this.foodEntries.length
      );

    } catch (error) {
      console.error(
        'Unable to load food history:',
        error
      );

      this.historyErrorMessage =
        'Unable to load your food history. Please try again.';

    } finally {
      this.isLoadingHistory = false;
      this.cdr.detectChanges();
    }
  }

  get selectedFood(): FoodItem | undefined {
    return this.foodItems.find(
      food => food.id === this.selectedFoodId
    );
  }

  get estimatedEmissions(): number | null {
    const food = this.selectedFood;

    if (
      !food ||
      this.quantityGrams === null ||
      !Number.isFinite(this.quantityGrams) ||
      this.quantityGrams <= 0
    ) {
      return null;
    }

    return (
      (this.quantityGrams / 1000) *
      food.emission_factor_kg_co2e_per_kg
    );
  }

  get totalFoodEmissions(): number {
    return this.foodEntries.reduce(
      (total, entry) => total + Number(entry.emissions_kg_co2e || 0),
      0
    );
  }

  get totalFoodEntries(): number {
    return this.foodEntries.length;
  }

  async saveFoodEntry(): Promise<void> {
    this.errorMessage = '';
    this.historyErrorMessage = '';
    this.successMessage = '';
    this.savedEntry = null;

    if (!this.selectedFoodId) {
      this.errorMessage = 'Please select a food item.';
      return;
    }

    if (
      this.quantityGrams === null ||
      !Number.isFinite(this.quantityGrams) ||
      this.quantityGrams <= 0
    ) {
      this.errorMessage =
        'Please enter a quantity greater than zero grams.';
      return;
    }

    if (!this.activityDate) {
      this.errorMessage =
        'Please select the date you ate this food.';
      return;
    }

    this.isSaving = true;

    try {
      const savedEntry = await this.foodService.createFoodEntry({
        food_item_id: this.selectedFoodId,
        quantity_grams: this.quantityGrams,
        activity_date: this.activityDate
      });

      this.savedEntry = savedEntry;

      this.quantityGrams = null;
      this.selectedFoodId = '';

      await this.loadFoodEntries();

      if (!this.historyErrorMessage) {
        this.successMessage =
          'Food entry saved successfully.';
      } else {
        this.successMessage =
          'Food entry saved successfully, but your history could not be refreshed.';
      }

    } catch (error) {
      console.error(
        'Unable to save food entry:',
        error
      );

      this.errorMessage =
        'Unable to save your food entry. Please try again.';

    } finally {
      this.isSaving = false;
      this.cdr.detectChanges();
    }
  }

  async deleteFoodEntry(entry: FoodEntry): Promise<void> {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${entry.food_name_snapshot}" from your food history?`
    );

    if (!confirmed) {
      return;
    }

    this.errorMessage = '';
    this.historyErrorMessage = '';
    this.successMessage = '';

    this.deletingEntryId = entry.id;

    try {
      await this.foodService.deleteFoodEntry(entry.id);

      await this.loadFoodEntries();

      if (!this.historyErrorMessage) {
        this.successMessage =
          'Food entry deleted successfully.';
      } else {
        this.successMessage =
          'Food entry deleted successfully, but your history could not be refreshed.';
      }

    } catch (error) {
      console.error(
        'Unable to delete food entry:',
        error
      );

      this.errorMessage =
        'Unable to delete this food entry. Please try again.';

    } finally {
      this.deletingEntryId = null;
      this.cdr.detectChanges();
    }
  }
}
