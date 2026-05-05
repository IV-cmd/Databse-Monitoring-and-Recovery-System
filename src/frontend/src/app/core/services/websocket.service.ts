import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';

export interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

@Injectable({
  providedIn: 'root'
})
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messageSubject = new Subject<WebSocketMessage>();
  public messages$ = this.messageSubject.asObservable();

  connect(url: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        this.messageSubject.next(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      setTimeout(() => this.connect(url), 5000);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnect(): void {
    this.socket?.close();
    this.socket = null;
  }

  sendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}
