
import { FormsModule } from '@angular/forms';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import {
  EcoAssistantService,
  EcoRecommendation
} from '../services/eco-assistant.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

@Component({
  selector: 'app-eco-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './eco-assistant.html',
  styleUrl: './eco-assistant.css'
})
export class EcoAssistant implements OnInit {
  recommendations: EcoRecommendation[] = [];
  loading = true;
  errorMessage = '';

  chatMessages: ChatMessage[] = [];
  messageInput = '';
  chatLoading = false;
  chatError = '';

  constructor(
    private ecoAssistantService: EcoAssistantService,
    private changeDetector: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.loadRecommendations();
  }

  async loadRecommendations(): Promise<void> {
    this.loading = true;
    this.errorMessage = '';
    this.changeDetector.detectChanges();

    try {
      this.recommendations =
        await this.ecoAssistantService.getRecommendations();
    } catch (error) {
      console.error('Eco Assistant error:', error);
      this.errorMessage =
        'Unable to load recommendations. Please try again.';
    } finally {
      this.loading = false;
      this.changeDetector.detectChanges();
    }
  }

  async sendMessage(): Promise<void> {
    const message = this.messageInput.trim();

    if (!message || this.chatLoading) {
      return;
    }

    if (message.length > 2000) {
      this.chatError = 'Your message must be 2000 characters or fewer.';
      return;
    }

    this.chatMessages.push({
      role: 'user',
      content: message
    });

    this.messageInput = '';
    this.chatLoading = true;
    this.chatError = '';
    this.changeDetector.detectChanges();

    try {
      const response =
        await this.ecoAssistantService.sendMessage(message);

      this.chatMessages.push({
        role: 'assistant',
        content: response
      });
    } catch (error) {
      console.error('Eco Assistant chat error:', error);
      this.chatError =
        'Unable to get a response. Please try again.';
    } finally {
      this.chatLoading = false;
      this.changeDetector.detectChanges();
    }
  }
}
