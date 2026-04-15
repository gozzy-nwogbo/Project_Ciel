# Skill: google-calendar

Google Calendar integration for Open Brain Phase 4. Read events, check availability, detect conflicts. Strictly read-only: no create, update, delete, or respond operations under any circumstances.
Trigger phrases: "what's on my calendar", "am I free", "today's events", "next week's schedule", "calendar conflicts", "check availability".
Output artifact: formatted event listings and conflict reports in conversation.

---

# Google Calendar Integration Skill

> Open Brain Phase 4. Read events only. No create, modify, or delete under any circumstances.

## Permission Boundaries (from PRD Security Table)

| Operation | Allowed | Tool |
|-----------|---------|------|
| List calendars | Yes | `list_calendars` |
| List events | Yes | `list_events` |
| Get single event | Yes | `get_event` |
| Suggest free time | Yes | `suggest_time` |
| Create event | **NO** | Not wired. Tool exists but must never be called. |
| Update event | **NO** | Not wired. Tool exists but must never be called. |
| Delete event | **NO** | Not wired. Tool exists but must never be called. |
| Respond to event | **NO** | Not wired. Tool exists but must never be called. |

## Defaults

- **Timezone:** America/Toronto (EST/EDT)
- **Calendar:** Primary calendar unless user specifies otherwise
- **Order:** Events sorted by start time ascending

## Available Operations

### 1. Surface Today's Events

```
Tool: list_events
startTime: "YYYY-MM-DDT00:00:00"
endTime: "YYYY-MM-DDT23:59:59"
timeZone: "America/Toronto"
orderBy: "startTime"
```

Output format:
```
- HH:MM - HH:MM | Event title (location if present)
```

If no events, say "No events today."

### 2. Surface Next N Days

Same as above but with endTime set to N days from now.

Default: next 7 days. Group output by date:
```
## Mon, Apr 14
- 09:00 - 10:00 | Team standup
- 14:00 - 15:00 | 1:1 with manager

## Tue, Apr 15
- No events
```

### 3. Get Event Details

Given an event ID from list results, retrieve full details.

```
Tool: get_event
eventId: <id>
```

Surface: title, time, location, description, attendees, Google Meet link if present.

### 4. Detect Conflicts

Given a time window, identify overlapping events:

1. Call `list_events` for the time range
2. Compare start/end times of all returned events
3. Flag any pair where event A's end > event B's start (overlap)

Output format:
```
CONFLICT: "Event A" (09:00-10:30) overlaps with "Event B" (10:00-11:00)
  Overlap: 30 minutes (10:00-10:30)
```

### 5. Check Availability (Free/Busy)

For checking if a time slot is open:

```
Tool: suggest_time
attendeeEmails: ["primary"]
startTime: <window start>
endTime: <window end>
timeZone: "America/Toronto"
durationMinutes: <requested slot length>
```

Surface available slots. Useful for "Am I free Thursday afternoon?" queries.

### 6. List All Calendars

```
Tool: list_calendars
```

Surface: calendar name, ID, and whether it's primary. Use to identify non-primary calendars for targeted queries.

## Approval Pattern

Same as Gmail: surface information first, wait for instruction before any action. Calendar is read-only so there are no write actions to approve, but the pattern applies to recommendations. If the user asks "should I move this meeting?", surface the conflict analysis but do not suggest calling create/update/delete tools. Say: "Calendar is read-only in this integration. You would need to make that change directly in Google Calendar."

## Event Logging

Every Calendar tool call must be logged to the system event log:

```json
{
  "timestamp": "ISO-8601",
  "category": "integration",
  "action": "calendar_read | calendar_list | calendar_availability",
  "tool": "tool name",
  "reason": "why this action was taken",
  "permission_tier": "read-only",
  "result": "success | failure"
}
```

## What This Skill Does NOT Do

- Create events (tool exists but is never called)
- Update or modify events (tool exists but is never called)
- Delete events (tool exists but is never called)
- Respond to event invitations (tool exists but is never called)
- Send any notifications
- Suggest rescheduling by calling write tools
