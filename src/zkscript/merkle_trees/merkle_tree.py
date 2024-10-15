from tx_engine import Script

from src.zkscript.util.utility_scripts import nums_to_script


class MerkleTree:
    """class for merkle trees."""

    def __init__(self, root: str, hash_function: str):
        self.root = root
        assert set(hash_function.split(" ")).issubset(
            {"OP_RIPEMD160", "OP_SHA1", "OP_SHA256", "OP_HASH160", "OP_HASH256"}
        )
        self.hash_function = hash_function

    def locking_merkle_proof_one_path(
        self,
        nodes: list[str],
        is_nodes_left: list[bool],
        is_equal_verify: bool = False,
    ) -> Script:
        """Generate a locking script requiring knowledge of a specific leaf in a Merkle tree.

        Args:
            nodes: A list of string representing the hash values of nodes.
            is_nodes_left: A list of boolean values specifing if the value in the list node is a left child of the parent
                node. If is_nodes_left = True, the values are swapped to the correct position.
            is_equal_verify: a boolean function determining if the script terminates with OP_EQUAL or OP_EQUALVERIFY. Default to False

        Returns:
            A locking script verifying a specific path to the Merkle root.

        The function iterates through each node in the `nodes` list, adding a swap command if the next node is a left
        child.

        Note:
            - `self.hash_function` must be a combination of valid Bitcoin Script hash functions (e.g., `OP_SHA256`).
            - `self.root` must be set to the expected Merkle root to verify against.

        """

        assert len(nodes) == len(is_nodes_left)

        out = Script()

        for node, position in zip(nodes, is_nodes_left):
            out.append_pushdata(bytes.fromhex(node))
            if position:
                out += Script.parse_string("OP_SWAP")
            out += Script.parse_string("OP_CAT")
            out += Script.parse_string(self.hash_function)

        out.append_pushdata(bytes.fromhex(self.root))
        out += Script.parse_string("OP_EQUALVERIFY") if is_equal_verify else Script.parse_string("OP_EQUAL")

        return out

    def locking_merkle_proof_any(
        self,
        depth: int,
        is_equal_verify: bool = False,
    ) -> Script:
        """Generate a script to verify a Merkle path of a certain lenght.

        Args:
            depth: An integer describing the depth of the Merkle treepresenting hash values of nodes in a Merkle tree.
            is_equal_verify: a boolean function determining if the script terminates with OP_EQUAL or OP_EQUALVERIFY. Default to False

        Returns:
            A locking script verifying any valid path to the Merkle root.

        The function generates a locking script that can be unlocked by valid Merkle path of length `depth`.

        Note:
            - `self.hash_function` must be a combination of valid Bitcoin Script hash functions (e.g., `OP_SHA256`).
            - `self.root` must be set to the expected Merkle root to verify against.

        """

        assert depth > 0

        out = Script.parse_string("OP_CAT")
        out += Script.parse_string(self.hash_function)

        for _ in range(depth - 1):
            out += Script.parse_string("OP_SWAP OP_CAT OP_CAT")
            out += Script.parse_string(self.hash_function)

        out.append_pushdata(bytes.fromhex(self.root))

        out += Script.parse_string("OP_EQUALVERIFY") if is_equal_verify else Script.parse_string("OP_EQUAL")

        return out

    def unlocking_merkle_proof_one_path(
        self,
        node: str,
    ) -> Script:
        """Generate a locking script requiring knowledge of a specific leaf in a Merkle tree.

        Args:
            node: A string representing hash of a leave.

        Returns:
            The unlocking script for the script generated by locking_merkle_proof_one_path.

        Note:
            - `self.hash_function` must be a combination of valid Bitcoin Script hash functions (e.g., `OP_SHA256`).
            - `self.root` must be set to the expected Merkle root to verify against.

        """

        out = Script()

        out.append_pushdata(bytes.fromhex(node))

        return out

    def unlocking_merkle_proof_any(
        self,
        left_nodes: list[str],
        right_nodes: list[str],
    ) -> Script:
        """Generate a script to verify a Merkle path of a certain lenght.

        Args:
            left_nodes: A list of strings representing the left elements in the Merkle path. If the left element is not
                needed at that level, use 0. The element at the end of the list represent a leaf node.
            right_nodes: A list of strings representing the rifht elements in the Merkle path. If the right element is
                not needed at that level, use 0. The element at the end of the list represent a leaf node.


        Returns:
            The unlocking script for the script generated by locking_merkle_proof_one_path.

        Note:
            - `self.hash_function` must be a combination of valid Bitcoin Script hash functions (e.g., `OP_SHA256`).
            - `self.root` must be set to the expected Merkle root to verify against.

        """

        assert len(left_nodes) == len(right_nodes)

        out = Script()

        for left_node, right_node in zip(left_nodes, right_nodes):
            out.append_pushdata(bytes.fromhex(left_node))
            out.append_pushdata(bytes.fromhex(right_node))

        return out
