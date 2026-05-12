##############################################################
# LifeOS AI - Full System Test (PowerShell 5.1 compatible)
# Tests: 3 users, 6 moods, 3 plans, 3 feedbacks, history
##############################################################

$BASE = "http://localhost:8000/api/v1"

function Invoke-API {
    param($method, $path, $body = $null)
    $uri = "$BASE$path"
    try {
        if ($body) {
            $json = $body | ConvertTo-Json -Depth 5
            return Invoke-RestMethod -Method $method -Uri $uri -Body $json -ContentType "application/json" -ErrorAction Stop
        } else {
            return Invoke-RestMethod -Method $method -Uri $uri -ErrorAction Stop
        }
    } catch {
        $detail = ""
        if ($_.ErrorDetails.Message) {
            try { $detail = ($_.ErrorDetails.Message | ConvertFrom-Json).detail } catch { $detail = $_.ErrorDetails.Message }
        }
        Write-Host "  [ERROR] $method $path : $detail" -ForegroundColor Red
        return $null
    }
}

function Write-Step { param($text) Write-Host "`n=== $text ===" -ForegroundColor Cyan }
function Write-OK   { param($text) Write-Host "  [OK] $text" -ForegroundColor Green }
function Write-Info { param($text) Write-Host "  [..] $text" -ForegroundColor Yellow }

# -------------------------------------------------------
# 0. Health Check
# -------------------------------------------------------
Write-Step "0. Health Check"
try {
    $health = Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
    if ($health.status -eq "healthy") { Write-OK "Backend is healthy" }
    else { Write-Host "  Unexpected health status: $($health.status)"; exit 1 }
} catch {
    Write-Host "  [FAIL] Cannot reach backend. Is the server running?" -ForegroundColor Red
    exit 1
}

# -------------------------------------------------------
# 1. Create 3 Users
# -------------------------------------------------------
Write-Step "1. Creating 3 Users"

$userDefs = @(
    [PSCustomObject]@{ name="Priya Sharma";  email="priya@lifeos.test" },
    [PSCustomObject]@{ name="Alex Johnson";  email="alex@lifeos.test"  },
    [PSCustomObject]@{ name="Ravi Kumar";    email="ravi@lifeos.test"  }
)

$userIds = @()
foreach ($u in $userDefs) {
    $resp = Invoke-API "POST" "/users" $u
    if ($resp) {
        $userIds += [int]$resp.id
        Write-OK "User '$($resp.name)' created with ID=$($resp.id)"
    }
}

if ($userIds.Count -lt 3) {
    Write-Host "  [FAIL] Could not create all users. Exiting." -ForegroundColor Red
    exit 1
}

$u1 = $userIds[0]
$u2 = $userIds[1]
$u3 = $userIds[2]

# -------------------------------------------------------
# 2. Submit Moods (multiple per user)
# -------------------------------------------------------
Write-Step "2. Submitting Moods (2 per user)"

$moodInputs = @(
    [PSCustomObject]@{ uid=$u1; text="I am super stressed today bro, too much work piled up, feeling overwhelmed" },
    [PSCustomObject]@{ uid=$u1; text="Still tired from yesterday, meh, just dragging through the day" },
    [PSCustomObject]@{ uid=$u2; text="Feeling hyped and energetic! Ready to crush the gym and kill it at work today" },
    [PSCustomObject]@{ uid=$u2; text="Feeling calm and very focused, great energy, good sleep last night" },
    [PSCustomObject]@{ uid=$u3; text="yaar aaj bahut thaka hua hoon, raat ko neend nahi aayi bilkul" },
    [PSCustomObject]@{ uid=$u3; text="okay feeling a bit better now, neutral mood, lets just get through the day" }
)

foreach ($m in $moodInputs) {
    $resp = Invoke-API "POST" "/mood" ([PSCustomObject]@{ user_id=[int]$m.uid; text=$m.text })
    if ($resp) {
        $stress  = [math]::Round($resp.stress_score  * 100)
        $energy  = [math]::Round($resp.energy_score  * 100)
        $conf    = [math]::Round($resp.confidence    * 100)
        Write-OK "User $($m.uid) | mood='$($resp.mood)' stress=$stress% energy=$energy% conf=$conf%"
    }
}

# -------------------------------------------------------
# 3. Generate Daily Plans (one per user)
# -------------------------------------------------------
Write-Step "3. Generating Daily Plans (takes 5-15s per user via LLM)"

$today = (Get-Date).ToString("yyyy-MM-dd")
$planIdMap = @{}

foreach ($uid in $userIds) {
    Write-Info "Generating plan for User $uid on $today ..."
    $resp = Invoke-API "POST" "/daily-plan" ([PSCustomObject]@{ user_id=[int]$uid; date=$today })
    if ($resp) {
        $planIdMap[$uid] = $resp.plan_id
        $itemCount = if ($resp.plan) { $resp.plan.Count } else { 0 }
        $agentCount = if ($resp.agent_proposals) { $resp.agent_proposals.Count } else { 0 }
        Write-OK "User $uid | plan_id=$($resp.plan_id) | $itemCount tasks | $agentCount agent proposals"

        # Print truncated explanation
        if ($resp.explanation) {
            $expl = $resp.explanation
            if ($expl.Length -gt 120) { $expl = $expl.Substring(0, 120) + "..." }
            Write-Info "Explanation: $expl"
        }

        # Print schedule items
        if ($resp.plan -and $resp.plan.Count -gt 0) {
            Write-Host "  Schedule:" -ForegroundColor White
            foreach ($item in $resp.plan) {
                $time = ""
                $task = ""
                if ($item.PSObject.Properties["time"])  { $time = "[$($item.time)] " }
                if ($item.PSObject.Properties["task"])  { $task = $item.task } else { $task = "$item" }
                Write-Host "    $time$task" -ForegroundColor Gray
            }
        }

        # Print agent proposals
        if ($resp.agent_proposals -and $resp.agent_proposals.Count -gt 0) {
            Write-Host "  Agent Proposals:" -ForegroundColor White
            foreach ($ap in $resp.agent_proposals) {
                $pct = [math]::Round($ap.priority * 100)
                Write-Host "    [$($ap.agent)] $($ap.proposal) (priority=$pct%)" -ForegroundColor Gray
            }
        }
    }
}

# -------------------------------------------------------
# 4. Submit Feedback
# -------------------------------------------------------
Write-Step "4. Submitting Feedback"

$feedbackList = @(
    [PSCustomObject]@{ uid=$u1; rating="up";      comment="Great plan! The walk really calmed me down. Loved it.";    tasks=@("Morning meditation") },
    [PSCustomObject]@{ uid=$u2; rating="up";      comment="awesome plan, gym session was perfect for my energy level"; tasks=@("Gym workout") },
    [PSCustomObject]@{ uid=$u3; rating="neutral"; comment="plan was okay, could be a bit more adjusted to my tiredness"; tasks=@() }
)

foreach ($fb in $feedbackList) {
    $planRef = $planIdMap[[int]$fb.uid]
    if (-not $planRef) {
        Write-Info "Skipping feedback for User $($fb.uid) - no plan was generated"
        continue
    }
    $body = [PSCustomObject]@{
        user_id         = [int]$fb.uid
        plan_id         = [int]$planRef
        rating          = $fb.rating
        completed_tasks = $fb.tasks
        comments        = $fb.comment
    }
    $resp = Invoke-API "POST" "/feedback" $body
    if ($resp -and $resp.success) {
        Write-OK "User $($fb.uid) | rating='$($fb.rating)' | $($resp.message)"
    }
}

# -------------------------------------------------------
# 5. Read History for Each User
# -------------------------------------------------------
Write-Step "5. Reading History per User"

foreach ($uid in $userIds) {
    $resp = Invoke-API "GET" "/history?user_id=$uid"
    if ($resp) {
        $planCount = if ($resp.plans) { $resp.plans.Count } else { 0 }
        $moodCount = if ($resp.mood_logs) { $resp.mood_logs.Count } else { 0 }
        Write-OK "User $uid | $planCount plan(s) | $moodCount mood log(s)"

        foreach ($p in $resp.plans) {
            $itemCount = if ($p.plan) { $p.plan.Count } else { 0 }
            Write-Host "    Plan #$($p.id) | $itemCount tasks | created: $($p.created_at)" -ForegroundColor Gray
        }
        foreach ($log in $resp.mood_logs) {
            $s = [math]::Round($log.stress_score * 100)
            Write-Host "    Mood '$($log.mood)' | stress=$s% | $($log.created_at)" -ForegroundColor Gray
        }
    }
}

# -------------------------------------------------------
# 6. Summary
# -------------------------------------------------------
Write-Step "DONE - Full System Test Complete"
Write-Host "  Users      : $($userIds.Count)  (IDs: $($userIds -join ', '))" -ForegroundColor Green
Write-Host "  Moods      : $($moodInputs.Count)" -ForegroundColor Green
Write-Host "  Plans      : $($planIdMap.Count)"  -ForegroundColor Green
Write-Host "  Feedbacks  : $($feedbackList.Count)" -ForegroundColor Green
Write-Host ""
Write-Host "  DB file    : backend\lifeos.db"                    -ForegroundColor Yellow
Write-Host "  Swagger UI : http://localhost:8000/docs"           -ForegroundColor Yellow
Write-Host "  Frontend   : http://localhost:5173"                -ForegroundColor Yellow
