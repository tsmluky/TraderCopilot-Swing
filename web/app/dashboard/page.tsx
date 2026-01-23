import { DashboardOverview } from '@/components/dashboard/dashboard-overview'

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Overview</h1>
        <p className="text-muted-foreground">
          Monitor your swing trading signals and performance metrics
        </p>
      </div>

      {/* Dashboard Overview */}
      <DashboardOverview />
    </div>
  )
}
