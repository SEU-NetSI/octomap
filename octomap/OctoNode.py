import math

from Config import LOGGER, DEFAULT_LOGODDS, OCCUPANCY_LOGODDS, FREE_LOGODDS

NUM_NODES = 0

class OctoNode:
    def __init__(self):
        """
        Initiates a new OctoNode, the probability of non-leaf will be set as 0.
        """
        self._children = ()
        self._log_odds = DEFAULT_LOGODDS
        self._is_leaf = False

    @property
    def probability(self):
        """
        Returns:
            occupancy probability of node --- float
        """
        odds: float = math.pow(math.e, self._log_odds)
        probability: float = odds / (odds + 1)
        
        return probability
    
    def is_leaf(self):
        """
        Returns:
            whether this node is leaf --- bool
        """
        return self._is_leaf

    def has_children(self):
        """
        Returns:
            whether this is a leaf node --- bool
        """
        return self._children != ()

    def get_children(self):
        """
        Returns:
            node's childern --- tuple
        """
        return self._children

    def _split(self):
        """
        Splits the node into 8 child nodes.
        Child nodes are given the occupancy probability of this parent node as the initial probability
        """
        global NUM_NODES
        self._children = (
        OctoNode(), OctoNode(), OctoNode(),
        OctoNode(), OctoNode(), OctoNode(),
        OctoNode(), OctoNode())
        self._log_odds = DEFAULT_LOGODDS
        NUM_NODES += 8
        # write number to the file
        with open('num_nodes.txt', 'a') as f:
            f.write(str(NUM_NODES) + "\n")
    
    def _prune(self):
        """
        Prune own children.
        """
        global NUM_NODES
        self._log_odds = self._children[0].get_log_odds()
        temp = list(self._children)
        temp.clear()
        self._children = tuple(temp)
        self._is_leaf = True
        NUM_NODES -= 8

    def index(self, point, origin, width):
        """
        Calculates the index of the child containing point.

        Args:
            point: the coornidate of the child node --- (x,y,z): tuple
            origin: the origin coornidate of the parent node -- (x,y,z): tuple
            width: the width of the parent node --- int

        Returns:
            the index of the child --- int
        """
        if not self.contains(point, origin, width):
            raise ValueError('Point is not contained in node.')

        return (1 if point[0] >= origin[0] + width / 2 else 0) + \
               (2 if point[1] >= origin[1] + width / 2 else 0) + \
               (4 if point[2] >= origin[2] + width / 2 else 0)

    @staticmethod
    def contains(point, origin, width):
        """
        Returns:
            whether the point is contained by this node --- bool
        """
        return ((origin[0] <= point[0] < (origin[0] + width)) and \
                (origin[1] <= point[1] < (origin[1] + width)) and \
                (origin[2] <= point[2] < (origin[2] + width)))

    @staticmethod
    def cal_origin(index: int, origin: tuple, width: int):
        """
        Calculates the origin of the node with given index.

        Args:
            index: the index of the child node --- int
            origin: the origin coordinate of the parent node --- (x,y,z): tuple
            width: the width of the parent node --- int
        """
        hwidth: int = int(width / 2)
        node_origin = (origin[0] + (hwidth if index & 1 else 0),
                      origin[1] + (hwidth if index & 2 else 0),
                      origin[2] + (hwidth if index & 4 else 0))

        return node_origin

    def get_origin(self):
        return self.origin

    def update(self, point, diff_logodds, origin, width, max_depth):
        """
        Updates the node with a new observation.

        Args:
            point: the point coornidate of the observation --- (x,y,z): tuple
            diff_logodds: the difference value of logodds --- float
            origin: origin of this node --- (x,y,z): tuple
            width: width of this node --- int
            max_depth: maximum depth this node can be branched --- int
        """
        self.origin = origin
        if max_depth == 0:
            self._update_logodds(diff_logodds)
            self._is_leaf = True
        else:
            if not self.has_children():
                self._split()
            try:
                child_index: int = self.index(point, origin, width)
                self._children[child_index].update(point, diff_logodds, self.cal_origin(child_index, origin, width), 
                                                width / 2, max_depth - 1)         
                # TODO: need test (prune)
                if self._check_children_logodds():
                    self._prune()

            except ValueError as e:
                pass
                # LOGGER.error(e)
                # LOGGER.error(point)

    def _check_children_logodds(self):
        """
        Returns:
            whether the logodds of all children are the same and arrive thresholds --- bool
        """
        if self.has_children():
            log_odds = self._children[0].get_log_odds()
            if log_odds != FREE_LOGODDS and log_odds != OCCUPANCY_LOGODDS:
                return False
            for child in self._children:
                if child.get_log_odds() != log_odds:
                    return False
            return True
        else:
            return True

    def _update_logodds(self, diff_logodds):
        """
        Updates the occupancy probability in logodds of the leaf node.

        Args:
            diff_logodds: the difference value of logodds --- float
        """
        self._log_odds += diff_logodds
        if self._log_odds >= OCCUPANCY_LOGODDS:
            self._log_odds = OCCUPANCY_LOGODDS
        if self._log_odds <= FREE_LOGODDS:
            self._log_odds = FREE_LOGODDS

    def get_log_odds(self):
        return self._log_odds

    def probability_at(self, point, origin, width):
        """
        Args:
            point: point at which the occupancy needs to be calculated --- (x,y,z): tuple
            origin: origin of this node --- (x,y,z): tuple
            width: width of this node --- int

        Returns:
            occupancy probability of a given point.
        """
        if not self.has_children():
            return self.probability
        else:
            child_index = self.index(point, origin, width)
            return self._children[child_index].probability_at(point, self.cal_origin(child_index, origin, width), width / 2)
