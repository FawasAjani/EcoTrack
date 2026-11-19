
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

  selectedFoodId = '';
  quantityGrams: number | null = null;
  activityDate = this.getTodayDate();

  isLoading = true;
  isSaving = false;

  errorMessage = '';
  successMessage = '';

  savedEntry: FoodEntry | null = null;

  constructor(
    private foodService: FoodService,
    private cdr: ChangeDetectorRef
  ) {}

  async ngOnInit(): Promise<void> {
    await this.loadFoodItems();
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

  async saveFoodEntry(): Promise<void> {
    this.errorMessage = '';
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

      this.successMessage =
        'Food entry saved successfully.';

      this.quantityGrams = null;
      this.selectedFoodId = '';

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
}
