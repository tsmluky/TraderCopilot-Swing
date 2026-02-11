'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Trash2, Plus, RefreshCw, Save, X } from "lucide-react"
import { toast } from "sonner"
import { changelogService, ChangelogEntry, ChangelogCreate } from "@/services/changelog"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"

export default function AdminChangelogPage() {
    const [entries, setEntries] = useState<ChangelogEntry[]>([])
    const [loading, setLoading] = useState(false)

    // New Entry State
    const [isDialogOpen, setIsDialogOpen] = useState(false)
    const [newEntry, setNewEntry] = useState<ChangelogCreate>({
        version: '',
        date: new Date().toISOString().split('T')[0],
        title: '',
        description: '',
        changes: [],
        type: 'minor'
    })
    const [changesText, setChangesText] = useState('')

    const fetchEntries = async () => {
        setLoading(true)
        try {
            const data = await changelogService.getChangelog()
            setEntries(data)
        } catch (error) {
            toast.error("Failed to load changelog")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchEntries()
    }, [])

    const handleCreate = async () => {
        try {
            // Parse changes text to array
            const changesList = changesText.split('\n').filter(line => line.trim() !== '')

            await changelogService.createEntry({
                ...newEntry,
                changes: changesList
            })

            toast.success("Changelog entry published")
            setIsDialogOpen(false)
            fetchEntries()

            // Reset form
            setNewEntry({
                version: '',
                date: new Date().toISOString().split('T')[0],
                title: '',
                description: '',
                changes: [],
                type: 'minor'
            })
            setChangesText('')

        } catch (error) {
            toast.error("Failed to publish entry")
            console.error(error)
        }
    }

    const handleDelete = async (version: string) => {
        if (!confirm(`Are you sure you want to delete version ${version}?`)) return

        try {
            await changelogService.deleteEntry(version)
            toast.success("Entry deleted")
            fetchEntries()
        } catch (error) {
            toast.error("Failed to delete entry")
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Changelog Management</h2>
                    <p className="text-muted-foreground">Manage application updates and release notes.</p>
                </div>
                <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>
                            <Plus className="mr-2 h-4 w-4" />
                            New Release
                        </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-xl">
                        <DialogHeader>
                            <DialogTitle>Publish New Release</DialogTitle>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Version</Label>
                                    <Input
                                        placeholder="1.2.0"
                                        value={newEntry.version}
                                        onChange={e => setNewEntry({ ...newEntry, version: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <Label>Date</Label>
                                    <Input
                                        type="date"
                                        value={newEntry.date}
                                        onChange={e => setNewEntry({ ...newEntry, date: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Type</Label>
                                    <Select
                                        value={newEntry.type}
                                        onValueChange={val => setNewEntry({ ...newEntry, type: val })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="major">Major</SelectItem>
                                            <SelectItem value="minor">Minor</SelectItem>
                                            <SelectItem value="patch">Patch</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label>Title</Label>
                                <Input
                                    placeholder="Release Title"
                                    value={newEntry.title}
                                    onChange={e => setNewEntry({ ...newEntry, title: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Description</Label>
                                <Textarea
                                    placeholder="Brief summary of the update..."
                                    value={newEntry.description}
                                    onChange={e => setNewEntry({ ...newEntry, description: e.target.value })}
                                />
                            </div>

                            <div className="space-y-2">
                                <Label>Changes (One per line)</Label>
                                <Textarea
                                    className="min-h-[150px] font-mono text-xs"
                                    placeholder="- Added feature X&#10;- Fixed bug Y"
                                    value={changesText}
                                    onChange={e => setChangesText(e.target.value)}
                                />
                            </div>

                            <Button onClick={handleCreate} className="w-full">
                                <Save className="mr-2 h-4 w-4" />
                                Publish Release
                            </Button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="grid gap-4">
                {entries.map((entry) => (
                    <Card key={entry.id} className="relative overflow-hidden group">
                        <div className={`absolute left-0 top-0 bottom-0 w-1 ${entry.type === 'major' ? 'bg-primary' :
                                entry.type === 'minor' ? 'bg-blue-500' : 'bg-muted-foreground/30'
                            }`} />

                        <CardHeader className="pb-2 pl-6">
                            <div className="flex items-start justify-between">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <CardTitle className="text-xl">v{entry.version}</CardTitle>
                                        <Badge variant="outline">{entry.type}</Badge>
                                        <span className="text-sm text-muted-foreground">{entry.date}</span>
                                    </div>
                                    <CardDescription className="text-base font-medium text-foreground/90">
                                        {entry.title}
                                    </CardDescription>
                                </div>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="text-muted-foreground hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => handleDelete(entry.version)}
                                >
                                    <Trash2 className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardHeader>
                        <CardContent className="pl-6 text-sm text-muted-foreground">
                            <p className="mb-2">{entry.description}</p>
                            <ul className="list-disc list-inside space-y-1 ml-1 opacity-80">
                                {/* Handle case where changes might be string if not parsed correctly by service, though service expects array */}
                                {Array.isArray(entry.changes) && entry.changes.map((change, i) => (
                                    <li key={i}>{change}</li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                ))}

                {!loading && entries.length === 0 && (
                    <div className="text-center py-10 text-muted-foreground border-2 border-dashed rounded-xl">
                        No changelog entries found. Create your first release!
                    </div>
                )}
            </div>
        </div>
    )
}
