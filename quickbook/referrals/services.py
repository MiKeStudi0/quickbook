from collections import deque
from django.db import transaction
from .models import ReferralNode

def get_or_create_referral_node(user):
    node, _ = ReferralNode.objects.get_or_create(user=user)
    return node

def place_user_in_referral_tree(new_user, referrer_user):
    """
    Places new_user under referrer_user's referral binary tree using Level-Order BFS traversal.
    Strategy:
    - Checks referrer's left position first.
    - If occupied, checks referrer's right position.
    - If both are occupied, traverses level-by-level left-to-right to find the first open spot.
    """
    with transaction.atomic():
        new_node = get_or_create_referral_node(new_user)

        if not referrer_user:
            return new_node

        referrer_node = get_or_create_referral_node(referrer_user)

        queue = deque([referrer_node])
        while queue:
            current = queue.popleft()

            if current.left is None:
                current.left = new_node
                current.save(update_fields=['left'])
                new_node.parent = current
                new_node.save(update_fields=['parent'])
                break
            elif current.right is None:
                current.right = new_node
                current.save(update_fields=['right'])
                new_node.parent = current
                new_node.save(update_fields=['parent'])
                break
            else:
                queue.append(current.left)
                queue.append(current.right)

        return new_node

def count_subtree_nodes(node):
    """
    Calculates total number of nodes in node's subtree (excluding node itself).
    """
    if not node:
        return 0

    count = 0
    queue = deque()
    if node.left:
        queue.append(node.left)
    if node.right:
        queue.append(node.right)

    while queue:
        curr = queue.popleft()
        count += 1
        if curr.left:
            queue.append(curr.left)
        if curr.right:
            queue.append(curr.right)

    return count

def get_team_stats(node):
    """
    Returns left_team_count, right_team_count, and total_team_count for a given ReferralNode.
    """
    if not node:
        return {
            "user_id": None,
            "username": None,
            "left_team_count": 0,
            "right_team_count": 0,
            "total_team_count": 0,
            "left_count": 0,
            "right_count": 0,
            "total_network": 0,
        }

    left_count = (1 + count_subtree_nodes(node.left)) if node.left else 0
    right_count = (1 + count_subtree_nodes(node.right)) if node.right else 0

    return {
        "user_id": node.user.id,
        "username": node.user.username,
        "left_team_count": left_count,
        "right_team_count": right_count,
        "total_team_count": left_count + right_count,
        "left_count": left_count,
        "right_count": right_count,
        "total_network": left_count + right_count,
    }


def find_root_node(node):
    """
    Finds top-most root node by ascending parent references.
    """
    curr = node
    while curr and curr.parent:
        curr = curr.parent
    return curr

def build_tree_dict(node):
    """
    Recursively builds a dictionary representation of the referral binary tree.
    """
    if not node:
        return None

    return {
        "id": node.id,
        "user_id": node.user.id,
        "username": node.user.username,
        "email": node.user.email,
        "referral_code": node.user.referral_code,
        "left": build_tree_dict(node.left),
        "right": build_tree_dict(node.right),
    }
