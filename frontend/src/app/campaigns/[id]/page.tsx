"use client";

import { useEffect, useState, use } from "react";
import { getCampaign, uploadResume, uploadTargets, processAllTargets, sendTargetEmail, updateTarget, sendAllApprovedTargets, deleteCampaign, approveAllTargets, updateCampaign } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Loader2, UploadCloud, RefreshCw, Send, Play, Edit, Check, Trash2, CheckCircle, Save } from "lucide-react";
import { useRouter } from "next/navigation";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";

export default function CampaignDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = use(params);
  const campaignId = parseInt(resolvedParams.id);
  
  const [campaign, setCampaign] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [targetFile, setTargetFile] = useState<File | null>(null);
  
  const [uploadingResume, setUploadingResume] = useState(false);
  const [uploadingTargets, setUploadingTargets] = useState(false);
  
  // Settings state
  const [subjectType, setSubjectType] = useState("personalized");
  const [constantSubject, setConstantSubject] = useState("");
  const [signature, setSignature] = useState("");
  const [context, setContext] = useState("");
  const [attachResume, setAttachResume] = useState(false);
  const [savingSettings, setSavingSettings] = useState(false);

  const [editingTarget, setEditingTarget] = useState<any>(null);
  
  const router = useRouter();

  const loadData = (initForm = false) => {
    getCampaign(campaignId)
      .then((data) => {
        setCampaign(data);
        if (initForm) {
          setSubjectType(data.subject_type || "personalized");
          setConstantSubject(data.constant_subject || "");
          setSignature(data.signature || "");
          setContext(data.context || "");
          setAttachResume(data.attach_resume || false);
        }
      })
      .catch(() => toast.error("Failed to load campaign"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData(true);
    const interval = setInterval(() => loadData(false), 5000);
    return () => clearInterval(interval);
  }, [campaignId]);

  const handleResumeUpload = async () => {
    if (!resumeFile) return;
    setUploadingResume(true);
    try {
      await uploadResume(campaignId, resumeFile);
      toast.success("Resume uploaded successfully");
      loadData();
    } catch (err) {
      toast.error("Failed to upload resume");
    } finally {
      setUploadingResume(false);
    }
  };

  const handleTargetUpload = async () => {
    if (!targetFile) return;
    setUploadingTargets(true);
    try {
      await uploadTargets(campaignId, targetFile);
      toast.success("Targets uploaded successfully");
      loadData();
    } catch (err) {
      toast.error("Failed to upload targets");
    } finally {
      setUploadingTargets(false);
    }
  };

  const handleSaveSettings = async () => {
    setSavingSettings(true);
    try {
      await updateCampaign(campaignId, {
        subject_type: subjectType,
        constant_subject: constantSubject,
        signature: signature,
        context: context,
        attach_resume: attachResume
      });
      toast.success("Campaign settings saved!");
      loadData();
    } catch (e) {
      toast.error("Failed to save campaign settings");
    } finally {
      setSavingSettings(false);
    }
  }

  const handleProcessAll = async () => {
    try {
      await updateCampaign(campaignId, {
        subject_type: subjectType,
        constant_subject: constantSubject,
        signature: signature,
        context: context,
        attach_resume: attachResume
      });
      await processAllTargets(campaignId);
      toast.success("Processing started. This will take a few minutes.");
      loadData();
    } catch (err) {
      toast.error("Failed to start processing");
    }
  };
  
  const handleApproveEdit = async () => {
    if (!editingTarget) return;
    try {
      await updateTarget(editingTarget.id, {
        ai_generated_subject: editingTarget.ai_generated_subject,
        ai_generated_body: editingTarget.ai_generated_body,
        status: "Approved"
      });
      toast.success("Email approved!");
      setEditingTarget(null);
      loadData();
    } catch (err) {
      toast.error("Failed to update target");
    }
  };

  const handleApproveAll = async () => {
    try {
      await approveAllTargets(campaignId);
      toast.success("All drafts have been approved!");
      loadData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to approve all targets");
    }
  };

  const handleSend = async (targetId: number) => {
    try {
      await updateCampaign(campaignId, {
        subject_type: subjectType,
        constant_subject: constantSubject,
        signature: signature,
        context: context,
        attach_resume: attachResume
      });
      await sendTargetEmail(targetId);
      toast.success("Email queued for sending");
      loadData();
    } catch (err) {
      toast.error("Failed to send email");
    }
  };

  const handleSendAll = async () => {
    try {
      await updateCampaign(campaignId, {
        subject_type: subjectType,
        constant_subject: constantSubject,
        signature: signature,
        context: context,
        attach_resume: attachResume
      });
      await sendAllApprovedTargets(campaignId);
      toast.success("Mass mailing started! Emails will be sent with a 5-second delay.");
      loadData();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Failed to start mass mailing");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this campaign? All targets and drafts will be lost forever.")) return;
    try {
      await deleteCampaign(campaignId);
      toast.success("Campaign deleted");
      router.push("/campaigns");
    } catch (err) {
      toast.error("Failed to delete campaign");
    }
  };


  if (loading && !campaign) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin h-8 w-8 text-primary" /></div>;
  if (!campaign) return <div>Campaign not found</div>;

  return (
    <div className="space-y-6 max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500 pb-12">
      <div className="flex justify-between items-center bg-card p-4 rounded-xl shadow-sm border border-border/50">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">{campaign.name}</h1>
          <p className="text-sm text-muted-foreground mt-1">Configure options, upload targets, and generate personalized emails.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadData(true)}><RefreshCw className="h-4 w-4 mr-2" /> Refresh</Button>
          <Button onClick={handleProcessAll} disabled={!campaign.resume_file_path || !campaign.targets || campaign.targets.length === 0} className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md transition-all">
            <Play className="h-4 w-4 mr-2" /> Start Processing
          </Button>
          <Button 
            onClick={handleApproveAll} 
            disabled={!campaign.targets || !campaign.targets.some((t: any) => t.status === 'Draft Generated')}
            className="bg-green-600 hover:bg-green-700 text-white shadow-md transition-all"
          >
            <CheckCircle className="h-4 w-4 mr-2" /> Approve All
          </Button>
          <Button 
            onClick={handleSendAll} 
            disabled={!campaign.targets || !campaign.targets.some((t: any) => t.status === 'Approved')}
            className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-md transition-all"
          >
            <Send className="h-4 w-4 mr-2" /> Send All Approved
          </Button>
          <Button variant="destructive" onClick={handleDelete} className="shadow-md">
            <Trash2 className="h-4 w-4 mr-2" /> Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Step 1: Uploads */}
        <div className="space-y-6 col-span-1">
          <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95 transition-all hover:shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">1. Upload Resume</CardTitle>
              <CardDescription>PDF Format Only.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {campaign.resume_file_path ? (
                <div className="p-2.5 bg-green-500/10 text-green-600 text-sm font-medium rounded-md flex items-center border border-green-500/20">
                  <Check className="h-4 w-4 mr-2" /> Resume uploaded.
                </div>
              ) : (
                <div className="p-2.5 bg-yellow-500/10 text-yellow-600 text-sm font-medium rounded-md border border-yellow-500/20">
                  Resume is required before AI generation.
                </div>
              )}
              <div className="flex gap-2">
                <Input type="file" accept=".pdf" className="text-sm" onChange={(e) => setResumeFile(e.target.files?.[0] || null)} />
                <Button onClick={handleResumeUpload} disabled={uploadingResume || !resumeFile} size="icon">
                  {uploadingResume ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
                </Button>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95 transition-all hover:shadow-md">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">2. Upload Targets</CardTitle>
              <CardDescription>CSV or Excel file.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input type="file" accept=".csv,.xlsx,.xls" className="text-sm" onChange={(e) => setTargetFile(e.target.files?.[0] || null)} />
                <Button onClick={handleTargetUpload} disabled={uploadingTargets || !targetFile} size="icon">
                  {uploadingTargets ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
                </Button>
              </div>
              <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                <strong>Required:</strong> Name, Email.<br/>
                <strong>Dynamic:</strong> Any other columns (e.g. Org, Publications) will be fed to the AI.
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Step 2: Campaign Settings */}
        <div className="col-span-2">
          <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95 h-full flex flex-col transition-all hover:shadow-md">
            <CardHeader className="pb-3 border-b border-border/50 mb-4">
              <CardTitle className="text-lg flex justify-between items-center">
                3. Campaign Email Settings
                <Button size="sm" onClick={handleSaveSettings} disabled={savingSettings}>
                  {savingSettings ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />} Save
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5 flex-grow">
              <div className="flex flex-col gap-4">
                <div className="space-y-2">
                  <Label>Email Subject Type</Label>
                  <Select value={subjectType} onValueChange={(val) => val && setSubjectType(val)}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Subject Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="personalized">AI Personalized</SelectItem>
                      <SelectItem value="constant">Constant Subject</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                {subjectType === "constant" && (
                  <div className="space-y-2 animate-in fade-in duration-300">
                    <Label>Constant Subject Text</Label>
                    <Input 
                      placeholder="e.g. Inquiry regarding Internship" 
                      value={constantSubject} 
                      onChange={(e) => setConstantSubject(e.target.value)} 
                    />
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label>Additional AI Context / Instructions</Label>
                <Textarea 
                  placeholder="e.g. Focus on my machine learning projects..."
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  className="resize-none h-20 text-sm"
                />
              </div>

              <div className="space-y-2">
                <Label>Email Signature Block</Label>
                <Textarea 
                  placeholder={"Warm Regards,\nJohn Doe\nUniversity Name"}
                  value={signature}
                  onChange={(e) => setSignature(e.target.value)}
                  className="resize-none font-mono text-sm h-28"
                />
              </div>

              <div className="flex items-center space-x-2 bg-secondary/30 p-3 rounded-lg border">
                <Checkbox 
                  id="attachResume" 
                  checked={attachResume} 
                  onCheckedChange={(c) => setAttachResume(c === true)} 
                />
                <div className="grid gap-1.5 leading-none">
                  <label
                    htmlFor="attachResume"
                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                  >
                    Attach PDF Resume to Emails
                  </label>
                  <p className="text-xs text-muted-foreground">
                    If checked, the system will append "I have attached my resume..." to the email and attach the PDF.
                  </p>
                </div>
              </div>

            </CardContent>
          </Card>
        </div>
      </div>

      <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95 mt-6 transition-all hover:shadow-md">
        <CardHeader className="bg-muted/30 border-b pb-4">
          <CardTitle>4. Target List ({campaign.targets?.length || 0})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <div className="rounded-b-md overflow-hidden">
            <Table>
              <TableHeader className="bg-secondary/20">
                <TableRow>
                  <TableHead className="pl-6">Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Org/Role</TableHead>
                  <TableHead>Extra Details</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right pr-6">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {campaign.targets?.map((target: any) => (
                  <TableRow key={target.id} className="hover:bg-muted/30 transition-colors">
                    <TableCell className="font-medium pl-6">{target.name}</TableCell>
                    <TableCell className="text-muted-foreground">{target.email}</TableCell>
                    <TableCell className="text-muted-foreground">{target.organization} {target.designation_or_department ? `/ ${target.designation_or_department}` : ''}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {target.dynamic_data && (() => {
                        try {
                          const data = JSON.parse(target.dynamic_data);
                          return (
                            <div className="flex flex-wrap gap-1">
                              {Object.entries(data).map(([k, v]) => (
                                <div key={k} className="text-[10px] bg-secondary/40 text-secondary-foreground px-1.5 py-0.5 rounded border max-w-[150px] truncate" title={`${k}: ${String(v)}`}>
                                  <span className="font-semibold">{k}:</span> {String(v)}
                                </div>
                              ))}
                            </div>
                          );
                        } catch (e) {
                          return null;
                        }
                      })()}
                    </TableCell>
                    <TableCell>
                      <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                        target.status === 'Sent' ? 'bg-green-500/15 text-green-600 border border-green-500/20' :
                        target.status === 'Draft Generated' ? 'bg-blue-500/15 text-blue-600 border border-blue-500/20' :
                        target.status === 'Approved' ? 'bg-purple-500/15 text-purple-600 border border-purple-500/20' :
                        target.status.includes('Failed') ? 'bg-red-500/15 text-red-600 border border-red-500/20' :
                        'bg-gray-500/15 text-gray-600 border border-gray-500/20'
                      }`}>
                        {target.status}
                      </span>
                    </TableCell>
                    <TableCell className="text-right pr-6 space-x-2">
                      {target.status === "Draft Generated" && (
                        <Button size="sm" variant="outline" className="shadow-sm" onClick={() => setEditingTarget(target)}>
                          <Edit className="h-3.5 w-3.5 mr-1" /> Review
                        </Button>
                      )}
                      {target.status === "Approved" && (
                        <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm" onClick={() => handleSend(target.id)}>
                          <Send className="h-3.5 w-3.5 mr-1" /> Send
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {(!campaign.targets || campaign.targets?.length === 0) && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-12 text-muted-foreground">
                      <div className="flex flex-col items-center justify-center space-y-3">
                        <UploadCloud className="h-10 w-10 text-muted-foreground/40" />
                        <p>No targets added yet. Upload a list above.</p>
                      </div>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Dialog open={!!editingTarget} onOpenChange={(open) => !open && setEditingTarget(null)}>
        <DialogContent className="max-w-3xl border-border shadow-xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-xl">Review Email Draft: {editingTarget?.name}</DialogTitle>
          </DialogHeader>
          <div className="space-y-5 py-4">
            {editingTarget?.dynamic_data && (
              <div className="bg-muted/30 p-3 rounded-md border border-border">
                <Label className="text-muted-foreground font-semibold mb-2 block">Extracted Context from CSV/Excel</Label>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    try {
                      const data = JSON.parse(editingTarget.dynamic_data);
                      return Object.entries(data).map(([k, v]) => (
                        <div key={k} className="text-xs bg-primary/10 text-primary-foreground px-2 py-1 rounded border border-primary/20">
                          <span className="font-semibold text-primary/80">{k}:</span> <span className="text-foreground">{String(v)}</span>
                        </div>
                      ));
                    } catch (e) {
                      return <span className="text-xs text-muted-foreground">Invalid extra data</span>;
                    }
                  })()}
                </div>
              </div>
            )}
            <div className="space-y-2">
              <Label className="text-muted-foreground font-semibold">Subject Line</Label>
              <Input 
                className="font-medium text-md"
                value={editingTarget?.ai_generated_subject || ''} 
                onChange={(e) => setEditingTarget({...editingTarget, ai_generated_subject: e.target.value})} 
              />
            </div>
            <div className="space-y-2">
              <Label className="text-muted-foreground font-semibold">Email Body</Label>
              <Textarea 
                className="min-h-[300px] leading-relaxed resize-none p-4 font-serif text-md"
                value={editingTarget?.ai_generated_body || ''} 
                onChange={(e) => setEditingTarget({...editingTarget, ai_generated_body: e.target.value})} 
              />
            </div>
          </div>
          <DialogFooter className="border-t pt-4">
            <Button variant="ghost" onClick={() => setEditingTarget(null)}>Cancel</Button>
            <Button onClick={handleApproveEdit} className="bg-purple-600 hover:bg-purple-700 text-white font-bold px-8 shadow-md transition-all">
              <CheckCircle className="h-4 w-4 mr-2" /> Approve Draft
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
