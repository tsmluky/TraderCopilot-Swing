$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

$base = "http://127.0.0.1:8000"

function Ok($msg){ Write-Host "✅ $msg" -ForegroundColor Green }
function Warn($msg){ Write-Host "⚠️  $msg" -ForegroundColor Yellow }
function Fail($msg){ Write-Host "❌ $msg" -ForegroundColor Red }

function Invoke-Json($method, $url, $body=$null, $headers=@{}) {
  $params = @{
    Method = $method
    Uri    = $url
    Headers = $headers
  }
  if ($null -ne $body) {
    $params["Body"] = $body
    $params["ContentType"] = "application/json"
  }
  return Invoke-RestMethod @params
}

Write-Host "=== SMOKE LOCAL (backend) ===" -ForegroundColor Cyan

# 0) Health
try {
  $r = Invoke-WebRequest -Uri "$base/" -UseBasicParsing -TimeoutSec 10
  Ok "GET / -> $($r.StatusCode)"
} catch {
  Fail "GET / failed: $($_.Exception.Message)"
  exit 1
}

# 1) Register (idempotente-ish)
$rand = Get-Random -Minimum 10000 -Maximum 99999
$email = "smoke_$rand@test.local"
$pass  = "Passw0rd!$rand"
$name  = "Smoke $rand"

try {
  $reg = Invoke-Json "POST" "$base/auth/register" (@{ email=$email; password=$pass; name=$name } | ConvertTo-Json)
  Ok "POST /auth/register -> ok ($email)"
} catch {
  Warn "POST /auth/register -> $($_.Exception.Message) (puede ser ok si backend no permite dominio/valida distinto)"
}

# 2) Token
try {
  $form = "username=$([uri]::EscapeDataString($email))&password=$([uri]::EscapeDataString($pass))"
  $tok = Invoke-RestMethod -Method POST -Uri "$base/auth/token" -Body $form -ContentType "application/x-www-form-urlencoded"
  if (-not $tok.access_token) { throw "No access_token in response" }
  Ok "POST /auth/token -> got access_token"
} catch {
  Fail "POST /auth/token failed: $($_.Exception.Message)"
  exit 1
}

$hAuth = @{ Authorization = "Bearer $($tok.access_token)" }

# 3) /auth/users/me
try {
  $me = Invoke-RestMethod -Method GET -Uri "$base/auth/users/me" -Headers $hAuth
  Ok "GET /auth/users/me -> $($me.email)"
} catch {
  Fail "GET /auth/users/me failed: $($_.Exception.Message)"
  exit 1
}

# 4) Entitlements
try {
  $ent = Invoke-RestMethod -Method GET -Uri "$base/auth/me/entitlements" -Headers $hAuth
  Ok "GET /auth/me/entitlements -> tier=$($ent.tier)"
  Write-Host ("   allowed_tokens sample: " + (($ent.allowed_tokens | Select-Object -First 5) -join ", "))
  Write-Host ("   allowed_timeframes: " + (($ent.allowed_timeframes) -join ", "))
} catch {
  Fail "GET /auth/me/entitlements failed: $($_.Exception.Message)"
  exit 1
}

# 5) Marketplace list
try {
  $mk = Invoke-RestMethod -Method GET -Uri "$base/strategies/marketplace" -Headers $hAuth
  $count = ($mk | Measure-Object).Count
  Ok "GET /strategies/marketplace -> $count items"
} catch {
  Warn "GET /strategies/marketplace failed: $($_.Exception.Message)"
}

# 6) Analyze LITE (BTC 4H)
try {
  $body = @{ token="BTC"; timeframe="4H"; mode="LITE"; message="smoke" } | ConvertTo-Json
  $al = Invoke-Json "POST" "$base/analyze/lite" $body $hAuth
  Ok "POST /analyze/lite -> ok"
} catch {
  Warn "POST /analyze/lite failed: $($_.Exception.Message)"
}

# 7) Analyze PRO (debería 403 si no sos PRO)
try {
  $body = @{ token="BTC"; timeframe="4H"; user_message="smoke pro" } | ConvertTo-Json
  $ap = Invoke-Json "POST" "$base/analyze/pro" $body $hAuth
  Ok "POST /analyze/pro -> ok (si tu tier es PRO esto está bien)"
} catch {
  Warn "POST /analyze/pro -> $($_.Exception.Message) (si no sos PRO, 403 es esperado)"
}

# 8) Advisor chat (debería 403 si no sos PRO)
try {
  $body = @{ messages=@(@{ role="user"; content="smoke" }); context=@{} } | ConvertTo-Json -Depth 6
  $ac = Invoke-Json "POST" "$base/advisor/chat" $body $hAuth
  Ok "POST /advisor/chat -> ok (si tu tier es PRO esto está bien)"
} catch {
  Warn "POST /advisor/chat -> $($_.Exception.Message) (si no sos PRO, 403 es esperado)"
}

# 9) Logs recent
try {
  $lr = Invoke-RestMethod -Method GET -Uri "$base/logs/recent" -Headers $hAuth
  Ok "GET /logs/recent -> ok"
} catch {
  Warn "GET /logs/recent failed: $($_.Exception.Message)"
}

Write-Host "=== DONE ===" -ForegroundColor Cyan
