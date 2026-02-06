// Shim: boost_graph_adjacency_list.hpp
#ifndef FREECAD_ADJACENCY_LIST_HPP_WORKAROUND
#define FREECAD_ADJACENCY_LIST_HPP_WORKAROUND

#define BOOST_ALLOW_DEPRECATED_HEADERS
#include <boost/graph/adjacency_list.hpp>
#undef BOOST_ALLOW_DEPRECATED_HEADERS

#endif
