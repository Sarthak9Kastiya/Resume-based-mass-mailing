"use client";

import { useEffect, useState } from "react";
import { getCampaigns, createCampaign, deleteCampaign } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { format } from "date-fns";
import Link from "next/link";
import { toast } from "sonner";
import { Loader2, Trash2 } from "lucide-react";

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newCampaignName, setNewCampaignName] = useState("");
  const [creating, setCreating] = useState(false);

  const loadCampaigns = () => {
    setLoading(true);
    getCampaigns()
      .then(setCampaigns)
      .catch(() => toast.error("Failed to load campaigns"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleCreate = async () => {
    if (!newCampaignName.trim()) return;
    setCreating(true);
    try {
      const created = await createCampaign(newCampaignName);
      setCampaigns([created, ...campaigns]);
      setNewCampaignName("");
      toast.success("Campaign created successfully");
    } catch (err) {
      toast.error("Failed to create campaign");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this campaign? All targets and drafts will be lost forever.")) return;
    try {
      await deleteCampaign(id);
      setCampaigns(campaigns.filter(c => c.id !== id));
      toast.success("Campaign deleted");
    } catch (err) {
      toast.error("Failed to delete campaign");
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Campaigns</h1>
      </div>

      <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95">
        <CardHeader>
          <CardTitle>Create New Campaign</CardTitle>
          <CardDescription>Start a new outreach campaign by giving it a name.</CardDescription>
        </CardHeader>
        <CardContent className="flex gap-4">
          <Input 
            placeholder="e.g. Summer 2026 Internship Outreach" 
            value={newCampaignName} 
            onChange={(e) => setNewCampaignName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <Button onClick={handleCreate} disabled={creating || !newCampaignName.trim()}>
            {creating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Create
          </Button>
        </CardContent>
      </Card>

      {loading ? (
        <div className="flex h-32 items-center justify-center"><Loader2 className="animate-spin h-8 w-8 text-primary" /></div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((c) => (
            <Link href={`/campaigns/${c.id}`} key={c.id}>
              <Card className="hover:border-primary transition-colors cursor-pointer h-full border-border/50 shadow-sm backdrop-blur-sm bg-card/95">
                <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
                  <div>
                    <CardTitle className="line-clamp-1 text-lg">{c.name}</CardTitle>
                    <CardDescription>{format(new Date(c.created_at), 'MMM d, yyyy')}</CardDescription>
                  </div>
                  <Button variant="ghost" size="icon" className="text-red-500 hover:text-red-700 hover:bg-red-500/10 h-8 w-8 -mr-2" onClick={(e) => handleDelete(e, c.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Status</span>
                    <span className={`text-sm font-medium px-2 py-1 rounded-full ${c.status === 'Completed' ? 'bg-green-500/10 text-green-500' : 'bg-blue-500/10 text-blue-500'}`}>
                      {c.status}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
          {campaigns.length === 0 && (
            <div className="col-span-full text-center py-12 text-muted-foreground">
              No campaigns yet. Create one above to get started.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
