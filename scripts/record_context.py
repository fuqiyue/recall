"""Shared VER lifecycle and append-only commit evidence for CLI and audit."""

import re

from recall_common import CHANGE_ID_PATTERN, change_ledgers
from task_context import unfenced
from recall_audit.constants import CHANGE_STATUSES as ACTIVE_STATUSES
from recall_audit.textutil import change_blocks, control_values

COMMIT_PATTERNS = (
    r'^\s*-\s*after_commit\s*[：:]\s*`?(?:commit:)?([0-9a-f]{7,40})`?\s*$',
    r'关联\s*Commit\*{0,2}\s*[：:]\s*`?([0-9a-f]{7,40})`?',
    r'\bcode\s*:\s*commit\s*:\s*`?([0-9a-f]{7,40})`?',
    r'^\s*-\s*commit\s*[：:]\s*`?([0-9a-f]{7,40})`?\s*$',
)
VERSION_ID = re.compile(r'^ver-\d{8}-\d{3}$')


def active_change_controls(root):
    """Only unique live CHG bodies may establish a draft's provenance."""
    controls = {}
    duplicates = set()
    for _, ledger in change_ledgers(root):
        text = unfenced(ledger.read_text(encoding='utf-8'))
        headings = re.findall(rf'^##\s+({CHANGE_ID_PATTERN})(?=\s|:|：|$)', text, re.M | re.I)
        seen = set()
        for identity in headings:
            if identity.casefold() in seen:
                duplicates.add(identity.casefold())
            seen.add(identity.casefold())
        for identity, block in change_blocks(text).items():
            key = identity.casefold()
            if key in controls:
                duplicates.add(key)
            controls[key] = control_values(block)
    return {key: value for key, value in controls.items() if key not in duplicates}


def is_active_version_draft(values, record, active_controls):
    if values.get('immutable') != ['false']:
        return False
    identities = values.get('change_id', [])
    if len(identities) != 1:
        return False
    block = active_controls.get(identities[0].casefold(), {})
    revision = values.get('proposal_revision', [])
    return (
        len(block.get('status', [])) == 1
        and block['status'][0] in ACTIVE_STATUSES
        and len(revision) == 1
        and re.fullmatch(r'[1-9]\d*', revision[0]) is not None
        and revision == block.get('proposal_revision')
        and values.get('version_slug') == [record.stem.casefold()]
        and block.get('version_slug') == [record.stem.casefold()]
    )


def version_record_state(text, record, active_controls):
    values = control_values(unfenced(text))
    if values.get('immutable') == ['false']:
        return 'draft' if is_active_version_draft(values, record, active_controls) else 'invalid-draft'
    if 'immutable' in values and values['immutable'] != ['true']:
        return 'invalid-draft'
    return 'archived'


def record_commit_hash(text):
    text = unfenced(text)
    for pattern in COMMIT_PATTERNS:
        match = re.search(pattern, text, re.I | re.M)
        if match:
            return match.group(1)
    return ''


def commit_corrections(texts, states):
    """Read direct corrections; never mutate originals or treat drafts as evidence."""
    texts = {path: unfenced(text) for path, text in texts.items()}
    identities = {
        value for path, text in texts.items() if states.get(path) == 'archived'
        for value in control_values(text).get('version_id', []) if VERSION_ID.fullmatch(value)
    }
    evidence = {}
    for path, text in texts.items():
        fields = control_values(text)
        target = fields.get('corrects', [])
        identity = fields.get('version_id', [])
        if states.get(path) != 'archived' or fields.get('status') != ['correction']:
            continue
        if len(target) != 1 or target[0] not in identities or target == identity:
            continue
        filename = re.fullmatch(r'logic_version-(\d{8}-\d{3})-.+\.md', path.name, re.I)
        if not filename or identity != ['ver-' + filename.group(1)]:
            continue
        if len(fields.get('after_commit', [])) != 1:
            continue
        # A based_on/code baseline is not evidence of the implementation commit.
        match = re.search(COMMIT_PATTERNS[0], text, re.I | re.M)
        if match and len(identity) == 1:
            evidence.setdefault(target[0], []).append({
                'version_id': identity[0].upper(), 'path': path, 'commit': match.group(1),
            })
    return evidence
