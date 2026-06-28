"use client";

import { useEffect, useState } from "react";
import { getConfig, updateConfig, testSmtp, getApiKeys, createApiKey, deleteApiKey, updateApiKeyPriority } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Loader2, Save, Activity, Plus, Trash2, ArrowUp, ArrowDown } from "lucide-react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";



export default function SettingsPage() {
  const [config, setConfig] = useState<any>(null);
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyProvider, setNewKeyProvider] = useState("Anthropic");

  const [newKeyValue, setNewKeyValue] = useState("");
  const [addingKey, setAddingKey] = useState(false);

  const fetchData = async () => {
    try {
      const [configData, keysData] = await Promise.all([getConfig(), getApiKeys()]);
      setConfig(configData);
      setApiKeys(keysData);
    } catch (err) {
      toast.error("Failed to load settings");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setConfig({ ...config, [e.target.name]: e.target.value });
  };

  const getEffectiveConfig = () => {
    return {
      ...config,
      smtp_host: config?.smtp_host || 'smtp.gmail.com',
      smtp_port: config?.smtp_port || 587,
    };
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = getEffectiveConfig();
      await updateConfig(payload);
      toast.success("Settings saved successfully!");
    } catch (err) {
      toast.error("Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleTestSmtp = async () => {
    setTesting(true);
    try {
      const payload = getEffectiveConfig();
      await testSmtp(payload);
      toast.success("SMTP Connection successful! Test email sent.");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "SMTP Connection failed");
    } finally {
      setTesting(false);
    }
  };

  const handleAddKey = async () => {
    if (!newKeyName || !newKeyValue) {
      toast.error("Please fill all fields (Name, Key)");
      return;
    }

    setAddingKey(true);
    try {
      await createApiKey({
        name: newKeyName,
        provider: newKeyProvider,
        model_name: "",
        key_encrypted: newKeyValue,
        priority: apiKeys.length
      });
      toast.success("API Key added");
      setNewKeyName("");
      setNewKeyValue("");
      fetchData();
    } catch (err) {
      toast.error("Failed to add API key");
    } finally {
      setAddingKey(false);
    }
  };

  const handleDeleteKey = async (id: number) => {
    try {
      await deleteApiKey(id);
      toast.success("API Key removed");
      fetchData();
    } catch (err) {
      toast.error("Failed to delete key");
    }
  };

  const moveKey = async (index: number, direction: 'up' | 'down') => {
    if (direction === 'up' && index === 0) return;
    if (direction === 'down' && index === apiKeys.length - 1) return;

    const newKeys = [...apiKeys];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    // Swap
    const temp = newKeys[index];
    newKeys[index] = newKeys[targetIndex];
    newKeys[targetIndex] = temp;

    setApiKeys(newKeys);
    
    // Save new priorities to backend
    try {
      await Promise.all(newKeys.map((k, i) => updateApiKeyPriority(k.id, i)));
      toast.success("Failover priority updated");
    } catch (e) {
      toast.error("Failed to update priority");
      fetchData(); // revert
    }
  };

  if (loading) {
    return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin h-8 w-8 text-primary" /></div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
      
      <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95">
        <CardHeader>
          <CardTitle>Email Configuration (SMTP)</CardTitle>
          <CardDescription>
            Configure your email account to enable mass mailing. Note: If you are using Gmail, you MUST use a 16-character App Password.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Sender Name</Label>
              <Input name="sender_name" value={config?.sender_name || ''} onChange={handleChange} placeholder="e.g. John Doe" />
            </div>
            <div className="space-y-2">
              <Label>Sender Email</Label>
              <Input name="sender_email" value={config?.sender_email || ''} onChange={handleChange} placeholder="e.g. user@example.com" />
            </div>
            <div className="space-y-2">
              <Label>SMTP Host</Label>
              <Input name="smtp_host" value={config?.smtp_host || 'smtp.gmail.com'} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>SMTP Port</Label>
              <Input name="smtp_port" type="number" value={config?.smtp_port || 587} onChange={handleChange} />
            </div>
            <div className="space-y-2">
              <Label>SMTP Username</Label>
              <Input name="smtp_username" value={config?.smtp_username || ''} onChange={handleChange} placeholder="Usually your email" />
            </div>
            <div className="space-y-2">
              <Label>SMTP Password (App Password)</Label>
              <Input name="smtp_password_encrypted" type="password" value={config?.smtp_password_encrypted || ''} onChange={handleChange} />
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between border-t p-6">
          <Button variant="outline" onClick={handleTestSmtp} disabled={testing}>
            {testing ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Activity className="h-4 w-4 mr-2" />}
            Test Connection
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
            Save Settings
          </Button>
        </CardFooter>
      </Card>
      
      <Card className="border-border/50 shadow-sm backdrop-blur-sm bg-card/95">
        <CardHeader>
          <CardTitle>AI Provider Failover System</CardTitle>
          <CardDescription>
            Add as many API keys as you want. The system will use them in the exact order shown below. If the top provider fails, it seamlessly falls back to the next one.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-3">
            {apiKeys.length === 0 ? (
              <p className="text-sm text-muted-foreground italic">No API keys configured yet.</p>
            ) : (
              apiKeys.map((key, index) => (
                <div key={key.id} className="flex items-center gap-3 p-3 bg-secondary/30 border rounded-lg">
                  <div className="flex flex-col gap-1">
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => moveKey(index, 'up')} disabled={index === 0}>
                      <ArrowUp className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => moveKey(index, 'down')} disabled={index === apiKeys.length - 1}>
                      <ArrowDown className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex-1 grid grid-cols-3 gap-4 items-center">
                    <div className="font-semibold">{key.name}</div>
                    <div className="text-sm text-muted-foreground">{key.provider}</div>
                    <div className="text-sm text-muted-foreground truncate">sk-...{key.key_encrypted.slice(-4)}</div>
                  </div>
                  <Button variant="destructive" size="icon" onClick={() => handleDeleteKey(key.id)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))
            )}
          </div>

          <div className="border-t pt-6">
            <h3 className="font-medium mb-4">Add New Provider</h3>
            <div className="grid grid-cols-4 gap-3 items-end">
              <div className="space-y-2 col-span-1">
                <Label>Alias Name</Label>
                <Input value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="e.g. Main Claude" />
              </div>
              <div className="space-y-2 col-span-1">
                <Label>Provider</Label>
                <Select value={newKeyProvider} onValueChange={(val) => val && setNewKeyProvider(val)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select Provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Anthropic">Anthropic</SelectItem>
                    <SelectItem value="Gemini">Gemini</SelectItem>
                    <SelectItem value="OpenAI">OpenAI</SelectItem>
                    <SelectItem value="DeepSeek">DeepSeek</SelectItem>
                    <SelectItem value="OpenRouter">OpenRouter</SelectItem>
                    <SelectItem value="Groq">Groq</SelectItem>
                    <SelectItem value="Mistral">Mistral AI</SelectItem>
                    <SelectItem value="Perplexity">Perplexity</SelectItem>
                    <SelectItem value="Together">Together AI</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2 col-span-1">
                <Label>API Key</Label>
                <Input type="password" value={newKeyValue} onChange={(e) => setNewKeyValue(e.target.value)} placeholder="sk-..." />
              </div>
              <div className="col-span-1">
                <Button className="w-full" onClick={handleAddKey} disabled={addingKey}>
                  {addingKey ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                  Add Key
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
