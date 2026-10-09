"use client";
import { Component, ReactNode } from "react";
export default class ViewerBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  componentDidCatch(error: Error) {
    console.error("Viewer unavailable", error);
  }
  render() {
    return this.state.failed ? (
      <main className="loading">
        <div className="loading-card">
          <h1>Let’s try again.</h1>
          <p>
            The property couldn’t be displayed on this device. Close other tabs,
            enable graphics acceleration, and reload.
          </p>
          <button onClick={() => location.reload()}>Reload walkthrough</button>
        </div>
      </main>
    ) : (
      this.props.children
    );
  }
}
