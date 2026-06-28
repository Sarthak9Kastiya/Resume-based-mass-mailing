export default function Dashboard() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
      <p className="text-muted-foreground text-lg">
        Welcome to the AI-Powered Hyper-Personalized Outreach & Mass Mailing Engine.
      </p>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mt-8">
        <div className="rounded-xl border bg-card text-card-foreground shadow-sm p-6 hover:shadow-md transition-shadow">
          <h3 className="font-semibold leading-none tracking-tight mb-2">Create Campaign</h3>
          <p className="text-sm text-muted-foreground mb-4">Start a new personalized mailing campaign.</p>
          <a href="/campaigns" className="text-sm font-medium text-primary hover:underline">View Campaigns &rarr;</a>
        </div>
      </div>
    </div>
  );
}
