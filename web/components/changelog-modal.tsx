'use client'

import { useState, useEffect } from 'react'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogTrigger
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Sparkles, GitCommit, Calendar, Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
// import { CHANGELOG_DATA } from "@/data/changelog" // Replaced by API
import { changelogService, ChangelogEntry } from '@/services/changelog'

export function ChangelogModal() {
    const [open, setOpen] = useState(false)
    const [hasNewUpdates, setHasNewUpdates] = useState(false)
    const [entries, setEntries] = useState<ChangelogEntry[]>([])
    const [loading, setLoading] = useState(false)

    // Check for updates and fetch data
    useEffect(() => {
        const fetchChangelog = async () => {
            setLoading(true)
            try {
                const data = await changelogService.getChangelog()
                setEntries(data)

                const lastSeen = localStorage.getItem('changelog_last_seen')
                const latestVersion = data[0]?.version

                if (latestVersion && lastSeen !== latestVersion) {
                    setHasNewUpdates(true)
                }
            } catch (error) {
                console.error("Failed to fetch changelog", error)
            } finally {
                setLoading(false)
            }
        }

        fetchChangelog()
    }, [])

    const handleOpenChange = (newOpen: boolean) => {
        setOpen(newOpen)
        if (newOpen) {
            const latestVersion = entries[0]?.version
            if (latestVersion) {
                localStorage.setItem('changelog_last_seen', latestVersion)
                setHasNewUpdates(false)
            }
        }
    }

    return (
        <Dialog open={open} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    className="gap-2 relative text-muted-foreground hover:text-foreground"
                    title="What's New"
                >
                    <Sparkles className={cn("h-4 w-4", hasNewUpdates ? "text-indigo-500 fill-indigo-500/20" : "")} />
                    <span className="hidden sm:inline">What's New</span>
                    {hasNewUpdates && (
                        <span className="absolute top-1.5 right-1.5 flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                        </span>
                    )}
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[85vh] flex flex-col p-0 gap-0 overflow-hidden">
                <div className="p-6 pb-2 border-b border-border/50 bg-muted/20">
                    <DialogHeader>
                        <DialogTitle className="flex items-center gap-2 text-xl">
                            <Sparkles className="h-5 w-5 text-indigo-500" />
                            Changelog
                        </DialogTitle>
                        <DialogDescription>
                            Stay updated with the latest improvements and features.
                        </DialogDescription>
                    </DialogHeader>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {loading && (
                        <div className="flex items-center justify-center py-10">
                            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                        </div>
                    )}

                    {!loading && entries.length === 0 && (
                        <div className="text-center text-muted-foreground py-10">
                            No updates found.
                        </div>
                    )}

                    {entries.map((entry) => (
                        <div key={entry.version} className="relative pl-4 border-l-2 border-muted">
                            <div className="absolute -left-[9px] top-0 h-4 w-4 rounded-full bg-background border-2 border-muted-foreground/30 ring-4 ring-background" />

                            <div className="flex flex-col gap-1 -mt-1 mb-4">
                                <div className="flex items-center gap-3">
                                    <span className="text-lg font-bold tracking-tight">v{entry.version}</span>
                                    <Badge variant={entry.type === 'major' ? 'default' : 'secondary'} className="uppercase text-[10px]">
                                        {entry.type}
                                    </Badge>
                                    <span className="text-xs text-muted-foreground flex items-center gap-1 ml-auto">
                                        <Calendar className="h-3 w-3" />
                                        {entry.date}
                                    </span>
                                </div>
                                <h3 className="text-base font-semibold text-foreground/90">{entry.title}</h3>
                                <p className="text-sm text-muted-foreground">{entry.description}</p>
                            </div>

                            <ul className="space-y-2 mt-3">
                                {entry.changes.map((change, i) => (
                                    <li key={i} className="text-sm flex items-start gap-2 text-muted-foreground/90">
                                        <GitCommit className="h-4 w-4 shrink-0 mt-0.5 opacity-50" />
                                        <span>{change}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </DialogContent>
        </Dialog>
    )
}
