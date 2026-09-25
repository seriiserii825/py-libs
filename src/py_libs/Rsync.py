import subprocess

from rich import print


class Rsync:
    """Thin rsync wrapper: local syncs and sshpass-authenticated transfers."""

    @staticmethod
    def _ssh_rsh(password: str, port: int | str) -> str:
        return (
            f"sshpass -p {password} ssh -p {port} "
            "-o StrictHostKeyChecking=accept-new"
        )

    @staticmethod
    def _build(
        flags: str,
        delete: bool,
        extra_args: list[str] | None,
        source: str,
        destination: str,
        rsh: str | None = None,
    ) -> list[str]:
        command = ["rsync", *flags.split()]
        if delete:
            command.append("--delete")
        if rsh:
            command.append(f"--rsh={rsh}")
        if extra_args:
            command.extend(extra_args)
        command.extend([source, destination])
        return command

    @staticmethod
    def _run(command: list[str]) -> subprocess.CompletedProcess:
        print(f"[dim]{' '.join(str(c) for c in command)}[/dim]")
        return subprocess.run(command, check=True)

    @staticmethod
    def local(
        source: str,
        destination: str,
        *,
        delete: bool = False,
        flags: str = "-av --progress",
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Sync between two local paths, no ssh involved."""
        command = Rsync._build(flags, delete, extra_args, source, destination)
        return Rsync._run(command)

    @staticmethod
    def push(
        source: str,
        remote_path: str,
        *,
        user: str,
        host: str,
        password: str,
        port: int | str = 22,
        delete: bool = False,
        flags: str = "-av --progress",
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Sync a local path to `user@host:remote_path` via sshpass."""
        rsh = Rsync._ssh_rsh(password, port)
        destination = f"{user}@{host}:{remote_path}"
        command = ["sshpass", "-p", password] + Rsync._build(
            flags, delete, extra_args, source, destination, rsh=rsh
        )
        return Rsync._run(command)

    @staticmethod
    def pull(
        remote_path: str,
        destination: str,
        *,
        user: str,
        host: str,
        password: str,
        port: int | str = 22,
        delete: bool = False,
        flags: str = "-av --progress",
        extra_args: list[str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Sync `user@host:remote_path` to a local destination via sshpass."""
        rsh = Rsync._ssh_rsh(password, port)
        source = f"{user}@{host}:{remote_path}"
        command = ["sshpass", "-p", password] + Rsync._build(
            flags, delete, extra_args, source, destination, rsh=rsh
        )
        return Rsync._run(command)
