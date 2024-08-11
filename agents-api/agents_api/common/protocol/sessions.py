"""
This module defines session-related data structures and settings used across the agents API.
It includes definitions for session settings and session data models.
"""

from uuid import UUID

from pydantic import BaseModel

from ...autogen.openapi_model import (
    Agent,
    ChatSettings,
    Session,
    Tool,
    User,
)
from .agents import AgentDefaultSettings


class SessionSettings(AgentDefaultSettings):
    """
    A placeholder for session-specific settings, inheriting from AgentDefaultSettings.
    Currently, it does not extend the base class with additional properties.
    """

    pass


class SessionData(BaseModel):
    """
    Represents the data associated with a session, including for agents, and users.
    """

    session: Session
    agents: list[Agent]
    users: list[User] = []
    settings: ChatSettings | None = None


class Toolset(BaseModel):
    agent_id: UUID
    tools: list[Tool]


class ChatContext(SessionData):
    """
    Represents the data associated with a context, including for agents, and users.
    """

    toolsets: list[Toolset]

    def get_active_agent(self) -> Agent:
        """
        Get the active agent from the session data.
        """
        requested_agent: UUID | None = self.settings.agent

        if requested_agent:
            assert requested_agent in [agent.id for agent in self.agents], (
                f"Agent {requested_agent} not found in session agents: "
                f"{[agent.id for agent in self.agents]}"
            )

            return next(agent for agent in self.agents if agent.id == requested_agent)

        return self.agents[0]

    def merge_settings(self, request_settings: ChatSettings):
        active_agent = self.get_active_agent()
        default_settings = active_agent.default_settings

        self.settings = ChatSettings(
            **{
                **default_settings.model_dump(),
                **request_settings.model_dump(exclude_unset=True),
            }
        )

    def get_active_tools(self) -> list[Tool]:
        """
        Get the active toolset from the session data.
        """
        active_agent = self.get_active_agent()
        active_toolset = next(
            toolset for toolset in self.toolsets if toolset.agent_id == active_agent.id
        )

        return active_toolset.tools

    def get_chat_environment(self) -> dict[str, dict | list[dict]]:
        """
        Get the chat environment from the session data.
        """
        current_agent = self.get_active_agent()
        tools = self.get_active_tools()

        return {
            "session": self.session.model_dump(),
            "agents": [agent.model_dump() for agent in self.agents],
            "current_agent": current_agent.model_dump(),
            "users": [user.model_dump() for user in self.users],
            "settings": self.settings.model_dump(),
            "tools": [tool.model_dump() for tool in tools],
        }
