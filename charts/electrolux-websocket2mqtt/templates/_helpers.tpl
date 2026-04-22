{{- define "electrolux-websocket2mqtt.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "electrolux-websocket2mqtt.fullname" -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "electrolux-websocket2mqtt.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "electrolux-websocket2mqtt.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "electrolux-websocket2mqtt.selectorLabels" -}}
app.kubernetes.io/name: {{ include "electrolux-websocket2mqtt.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "electrolux-websocket2mqtt.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "electrolux-websocket2mqtt.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{- define "electrolux-websocket2mqtt.configSecretName" -}}
{{- if .Values.config.existingSecret -}}
{{ .Values.config.existingSecret }}
{{- else -}}
{{ printf "%s-config" (include "electrolux-websocket2mqtt.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end -}}
{{- end -}}
