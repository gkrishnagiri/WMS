import { useMutation } from "@tanstack/react-query";
import { Alert, Button, Stack } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { handoffWithAgent } from "../../services/agentChatApi";

export function InvestigateWithAgentButton({
  sourceType,
  sourceId,
  label = "Investigate with Agent",
}: {
  sourceType: string;
  sourceId: string;
  label?: string;
}) {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: () => handoffWithAgent(sourceType, sourceId),
    onSuccess: (result) => navigate(result.agent_investigation_url || result.agent_chat_url),
  });
  return (
    <Stack direction="row" spacing={1} alignItems="center">
      <Button
        size="small"
        variant="outlined"
        onClick={() => mutation.mutate()}
        disabled={mutation.isPending}
      >
        {mutation.isPending ? "Starting…" : label}
      </Button>
      {mutation.error && (
        <Alert severity="error">{(mutation.error as Error).message}</Alert>
      )}
    </Stack>
  );
}
