import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Alert, Box, Button, Card, CardContent, Chip, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Typography } from "@mui/material";
import { generateGovernedContextSummary, generateGovernedCustomerUpdate, generateGovernedInvestigationChecklist, generateGovernedWorkNote, getSessionAiInvocations, type GovernedDraftResponse } from "../services/copilotApi";

type DraftType = "CONTEXT_SUMMARY" | "WORK_NOTE_DRAFT" | "CUSTOMER_UPDATE_DRAFT" | "INVESTIGATION_CHECKLIST";

const labels: Record<DraftType, string> = {
  CONTEXT_SUMMARY: "Generate Governed Context Summary",
  WORK_NOTE_DRAFT: "Generate Governed Work Note",
  CUSTOMER_UPDATE_DRAFT: "Generate Governed Customer Update",
  INVESTIGATION_CHECKLIST: "Generate Governed Investigation Checklist",
};

export function GovernedAiPanel({ sessionId, hasContext }: { sessionId: string; hasContext: boolean }) {
  const queryClient = useQueryClient();
  const [result, setResult] = useState<GovernedDraftResponse | null>(null);
  const invocations = useQuery({ queryKey: ["copilot", "ai-invocations", sessionId], queryFn: () => getSessionAiInvocations(sessionId), enabled: Boolean(sessionId) });
  const mutation = useMutation({
    mutationFn: (kind: DraftType) => kind === "CONTEXT_SUMMARY" ? generateGovernedContextSummary(sessionId) : kind === "WORK_NOTE_DRAFT" ? generateGovernedWorkNote(sessionId) : kind === "CUSTOMER_UPDATE_DRAFT" ? generateGovernedCustomerUpdate(sessionId) : generateGovernedInvestigationChecklist(sessionId),
    onSuccess: (data) => { setResult(data); void queryClient.invalidateQueries({ queryKey: ["copilot", "session", sessionId] }); void queryClient.invalidateQueries({ queryKey: ["copilot", "ai-invocations", sessionId] }); void queryClient.invalidateQueries({ queryKey: ["ai-config"] }); },
  });
  return <Card sx={{ mb: 3 }}><CardContent><Typography variant="h5">Governed AI Drafts</Typography><Typography color="text.secondary" sx={{ mt: 1 }}>These drafts use the governed AI provider gateway and deterministic mock provider. No external LLM call is made and no support action is applied automatically.</Typography><Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: "wrap" }}>{(Object.keys(labels) as DraftType[]).map(kind => <Button key={kind} variant={kind === "WORK_NOTE_DRAFT" ? "contained" : "outlined"} disabled={!hasContext || mutation.isPending} onClick={() => mutation.mutate(kind)}>{labels[kind]}</Button>)}</Stack>{!hasContext && <Alert severity="info" sx={{ mt: 2 }}>Build a context snapshot before generating governed drafts.</Alert>}{mutation.error && <Alert severity="error" sx={{ mt: 2 }}>{(mutation.error as Error).message}</Alert>}{result && <Box sx={{ mt: 3, p: 2, border: 1, borderColor: "divider", borderRadius: 1 }}><Typography variant="h6">{result.message.title}</Typography><Stack direction="row" spacing={1} sx={{ my: 1, flexWrap: "wrap" }}><Chip size="small" label={result.message.generation_mode || "GOVERNED_AI_MOCK"} /><Chip size="small" label={result.invocation.safety_status} color={result.invocation.safety_status === "BLOCKED" ? "error" : result.invocation.safety_status === "WARNED" ? "warning" : "success"} /><Chip size="small" label={result.invocation.task_type} /><Chip size="small" label={`${result.invocation.total_tokens_estimated} tokens`} /></Stack><Typography sx={{ whiteSpace: "pre-wrap" }}>{result.message.content}</Typography><Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>Invocation {result.invocation.invocation_number} · {result.invocation.status} · ${result.invocation.cost_estimated.toFixed(4)}</Typography>{result.invocation.blocked_reason && <Typography color="error" sx={{ mt: 1 }}>Blocked reason: {result.invocation.blocked_reason}</Typography>}</Box>}<Typography variant="h6" sx={{ mt: 3, mb: 1 }}>AI Invocation Audit</Typography><TableContainer><Table size="small"><TableHead><TableRow>{["Invocation", "Task", "Status", "Safety", "Tokens", "Created"].map(header => <TableCell key={header}>{header}</TableCell>)}</TableRow></TableHead><TableBody>{(invocations.data || []).map(row => <TableRow key={row.id}><TableCell>{row.invocation_number}</TableCell><TableCell>{row.task_type}</TableCell><TableCell>{row.status}</TableCell><TableCell>{row.safety_status}</TableCell><TableCell>{row.total_tokens_estimated}</TableCell><TableCell>{new Date(row.created_at).toLocaleString()}</TableCell></TableRow>)}</TableBody></Table></TableContainer>{invocations.error && <Alert severity="error" sx={{ mt: 2 }}>{(invocations.error as Error).message}</Alert>}</CardContent></Card>;
}
