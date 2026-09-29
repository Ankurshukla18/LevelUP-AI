'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { CATEGORIES, PRIORITIES } from '@/lib/constants';
import { goalsService } from '@/services/goals';
import { Sidebar } from '@/components/layout/sidebar';
import { roadmapService } from '@/services/roadmap';

export default function NewGoalPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: '',
    description: '',
    startDate: '',
    targetDate: '',
    currentLevel: '',
    targetOutcome: '',
    availableHoursPerWeek: '',
    priority: '',
    motivation: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSelectChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const newGoal = await goalsService.create({
        ...formData,
        availableHoursPerWeek: Number(formData.availableHoursPerWeek)
      });
      // Automatically generate roadmap
      await roadmapService.generate(newGoal.id);
      router.push(`/goals/${newGoal.id}`);
    } catch (error) {
      console.error(error);
      alert('Failed to create goal');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-3xl font-bold mb-8">Create New Goal</h1>
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="name">Goal Name <span className="text-red-500">*</span></Label>
                    <Input id="name" placeholder="e.g., Learn Full Stack Development" required value={formData.name} onChange={handleChange} />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="category">Category <span className="text-red-500">*</span></Label>
                    <Select onValueChange={(val) => handleSelectChange('category', val)} required>
                      <SelectTrigger><SelectValue placeholder="Select Category" /></SelectTrigger>
                      <SelectContent>
                        {CATEGORIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="priority">Priority <span className="text-red-500">*</span></Label>
                    <Select onValueChange={(val) => handleSelectChange('priority', val)} required>
                      <SelectTrigger><SelectValue placeholder="Select Priority" /></SelectTrigger>
                      <SelectContent>
                        {PRIORITIES.map(p => <SelectItem key={p} value={p}>{p}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="description">Description (Optional)</Label>
                    <Textarea id="description" placeholder="Briefly describe what you want to achieve" value={formData.description} onChange={handleChange} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="startDate">Start Date <span className="text-red-500">*</span></Label>
                    <Input id="startDate" type="date" required value={formData.startDate} onChange={handleChange} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="targetDate">Target Date <span className="text-red-500">*</span></Label>
                    <Input id="targetDate" type="date" required value={formData.targetDate} onChange={handleChange} />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="currentLevel">Current Level <span className="text-red-500">*</span></Label>
                    <Input id="currentLevel" placeholder="e.g., Beginner with HTML/CSS" required value={formData.currentLevel} onChange={handleChange} />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="targetOutcome">Target Outcome <span className="text-red-500">*</span></Label>
                    <Textarea id="targetOutcome" placeholder="e.g., Build a complete web app independently" required value={formData.targetOutcome} onChange={handleChange} />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="availableHoursPerWeek">Available Hours/Week <span className="text-red-500">*</span></Label>
                    <Input id="availableHoursPerWeek" type="number" min="1" max="168" required value={formData.availableHoursPerWeek} onChange={handleChange} />
                  </div>

                  <div className="space-y-2 col-span-2">
                    <Label htmlFor="motivation">Motivation (Optional)</Label>
                    <Input id="motivation" placeholder="Why is this important to you?" value={formData.motivation} onChange={handleChange} />
                  </div>
                </div>

                <div className="flex justify-end gap-4 pt-4 border-t">
                  <Button type="button" variant="outline" onClick={() => router.back()}>Cancel</Button>
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Creating...' : 'Create Goal & Generate Roadmap'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
