"use client";
import dynamic from "next/dynamic";
import ViewerBoundary from "../components/ViewerBoundary";
const Walkthrough = dynamic(() => import("../components/Walkthrough"), {
  ssr: false,
  loading: () => (
    <main className="loading">
      <p>Preparing your walkthrough…</p>
    </main>
  ),
});
export default function Page() {
  return (
    <ViewerBoundary>
      <Walkthrough />
    </ViewerBoundary>
  );
}
