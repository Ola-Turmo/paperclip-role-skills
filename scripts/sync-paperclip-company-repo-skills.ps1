param(
    [string]$BaseUrl = "http://vps-apimcp-site.tail928971.ts.net:13101"
)

$ErrorActionPreference = "Stop"

function Invoke-PaperclipJson {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("GET", "POST", "PATCH")]
        [string]$Method,
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [object]$Body
    )

    $headers = @{
        Origin  = $script:BaseUrl
        Referer = "$($script:BaseUrl)/"
    }

    $bodyJson = $null
    if ($null -ne $Body) {
        $headers["Content-Type"] = "application/json"
        $bodyJson = $Body | ConvertTo-Json -Depth 100
    }

    try {
        $response = Invoke-WebRequest -Method $Method -Uri "$($script:BaseUrl)$Path" -Headers $headers -Body $bodyJson -UseBasicParsing
        if ([string]::IsNullOrWhiteSpace($response.Content)) {
            return $null
        }
        return $response.Content | ConvertFrom-Json
    } catch {
        if (-not $_.Exception.Response) {
            throw
        }

        $reader = New-Object IO.StreamReader($_.Exception.Response.GetResponseStream())
        $bodyText = $reader.ReadToEnd()
        throw "HTTP $([int]$_.Exception.Response.StatusCode) for $Method $Path`n$bodyText"
    }
}

function Ensure-Workspace {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectId,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$RepoUrl,
        [string]$PackRole = "company-repo",
        [string]$RepoPurpose = "company-specific skill source"
    )

    $workspaces = @((Invoke-PaperclipJson -Method GET -Path "/api/projects/$ProjectId/workspaces" -Body $null))
    $existing = $workspaces | Where-Object { $_.repoUrl -eq $RepoUrl } | Select-Object -First 1
    $payload = @{
        name       = $Name
        sourceType = "git_repo"
        repoUrl    = $RepoUrl
        isPrimary  = $false
        metadata   = @{
            packRole    = $PackRole
            repoPurpose = $RepoPurpose
        }
    }

    if ($existing) {
        return Invoke-PaperclipJson -Method PATCH -Path "/api/projects/$ProjectId/workspaces/$($existing.id)" -Body $payload
    }

    return Invoke-PaperclipJson -Method POST -Path "/api/projects/$ProjectId/workspaces" -Body $payload
}

function Import-RepoSkills {
    param(
        [Parameter(Mandatory = $true)]
        [string]$CompanyId,
        [Parameter(Mandatory = $true)]
        [string]$RepoUrl
    )

    try {
        return [pscustomobject]@{
            repoUrl = $RepoUrl
            ok = $true
            result = Invoke-PaperclipJson -Method POST -Path "/api/companies/$CompanyId/skills/import" -Body @{ source = $RepoUrl }
            error = $null
        }
    } catch {
        return [pscustomobject]@{
            repoUrl = $RepoUrl
            ok = $false
            result = $null
            error = $_.Exception.Message
        }
    }
}

$companySpecs = @(
    @{
        CompanyName = "Personal"
        ProjectName = "Private Core Operating System"
        WorkspaceAdds = @()
        ImportRepos = @(
            "https://github.com/Ola-Turmo/paperclip-personal-admin",
            "https://github.com/Ola-Turmo/paperclip-private-life",
            "https://github.com/Ola-Turmo/paperclip-personal-health",
            "https://github.com/Ola-Turmo/paperclip-relationships"
        )
    },
    @{
        CompanyName = "Kurs.ing"
        ProjectName = "Passing and Conversion Engine"
        WorkspaceAdds = @(
            @{
                Name = "kurs.ing product repo"
                RepoUrl = "https://github.com/Ola-Turmo/kurs.ing"
                PackRole = "company-repo"
                RepoPurpose = "live Kurs.ing product and repo-native skills"
            }
        )
        ImportRepos = @(
            "https://github.com/Ola-Turmo/kurs.ing"
        )
    },
    @{
        CompanyName = "Gatareba.ge"
        ProjectName = "Reviewed Compliance Workspace"
        WorkspaceAdds = @(
            @{
                Name = "Gatareba.ge product repo"
                RepoUrl = "https://github.com/Ola-Turmo/Gatareba.ge"
                PackRole = "company-repo"
                RepoPurpose = "live Gatareba product and compliance skills"
            }
        )
        ImportRepos = @(
            "https://github.com/Ola-Turmo/Gatareba.ge"
        )
    },
    @{
        CompanyName = "Lovkode.no"
        ProjectName = "Matter Execution Core"
        WorkspaceAdds = @(
            @{
                Name = "lovkode.no product repo"
                RepoUrl = "https://github.com/Ola-Turmo/lovkode.no"
                PackRole = "company-repo"
                RepoPurpose = "live Lovkode product and legal-matter skills"
            }
        )
        ImportRepos = @(
            "https://github.com/Ola-Turmo/lovkode.no"
        )
    },
    @{
        CompanyName = "Parallel Company AI"
        ProjectName = "Global Platform Layer"
        WorkspaceAdds = @(
            @{
                Name = "curated plugin universe"
                RepoUrl = "https://github.com/Ola-Turmo/curated-paperclip-plugins"
                PackRole = "portfolio-curation"
                RepoPurpose = "portfolio repo-universe curation skill"
            }
        )
        ImportRepos = @(
            "https://github.com/Ola-Turmo/curated-paperclip-plugins"
        )
    },
    @{
        CompanyName = "EmDash Sidecar SaaS"
        ProjectName = "Sidecar Core Product"
        WorkspaceAdds = @()
        ImportRepos = @(
            "https://github.com/Ola-Turmo/emdash-astro-sidecar"
        )
    },
    @{
        CompanyName = "TRT.ge"
        ProjectName = "Authority Platform and Simulator Growth"
        WorkspaceAdds = @(
            @{
                Name = "trt.ge product repo"
                RepoUrl = "https://github.com/Ola-Turmo/trt.ge"
                PackRole = "company-repo"
                RepoPurpose = "live TRT.ge product and authority-growth skills"
            }
        )
        ImportRepos = @(
            "https://github.com/Ola-Turmo/trt.ge"
        )
    },
    @{
        CompanyName = "AI Influencer & Spokesperson Company"
        ProjectName = "Agency SaaS Platform"
        WorkspaceAdds = @()
        ImportRepos = @(
            "https://github.com/Ola-Turmo/paperclip-plugin-ai-spokesperson-agency"
        )
    }
)

$companies = @((Invoke-PaperclipJson -Method GET -Path "/api/companies" -Body $null))
$report = @()

foreach ($spec in $companySpecs) {
    $company = $companies | Where-Object { $_.name -eq $spec.CompanyName } | Select-Object -First 1
    if (-not $company) {
        throw "Company not found: $($spec.CompanyName)"
    }

    $projects = @((Invoke-PaperclipJson -Method GET -Path "/api/companies/$($company.id)/projects" -Body $null))
    $project = $projects | Where-Object { $_.name -eq $spec.ProjectName } | Select-Object -First 1
    if (-not $project) {
        throw "Project '$($spec.ProjectName)' not found in $($spec.CompanyName)"
    }

    foreach ($workspaceSpec in @($spec.WorkspaceAdds)) {
        Ensure-Workspace -ProjectId $project.id -Name $workspaceSpec.Name -RepoUrl $workspaceSpec.RepoUrl -PackRole $workspaceSpec.PackRole -RepoPurpose $workspaceSpec.RepoPurpose | Out-Null
    }

    $imports = @()
    foreach ($repoUrl in @($spec.ImportRepos)) {
        $imports += Import-RepoSkills -CompanyId $company.id -RepoUrl $repoUrl
    }

    $report += [pscustomobject]@{
        company = $spec.CompanyName
        companyId = $company.id
        project = $spec.ProjectName
        imported = $imports
    }
}

$report | ConvertTo-Json -Depth 8
