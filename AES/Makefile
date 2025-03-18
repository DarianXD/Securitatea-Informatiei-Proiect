# macOS build

CC := clang
STD := c17

CCFLAGS := 
LDFLAGS := 

WARNINGS := -Werror -Wpedantic -Wall -Wextra -Wconversion -Wstrict-prototypes -Wshadow

TARGET := libaes.dylib

BUILD_DIR := build

SRC_DIR := src
OBJ_DIR := $(BUILD_DIR)/obj
DEP_DIR := $(OBJ_DIR)/.deps

INCLUDE := -I$(SRC_DIR)

SRC := $(shell find $(SRC_DIR) -name '*.c')
OBJ := $(patsubst $(SRC_DIR)/%.c, $(OBJ_DIR)/%.o, $(SRC))
DEP := $(patsubst $(SRC_DIR)/%.c, $(DEP_DIR)/%.d, $(SRC))

$(TARGET): $(BUILD_DIR)/$(TARGET)

$(BUILD_DIR)/$(TARGET): $(OBJ)
	@mkdir -p $(@D)
	$(CC) $(LDFLAGS) -o $@ $^ -dynamiclib -install_name "$(TARGET)"

$(SRC_DIR)/%.o:
	$(MAKE) $(patsubst $(SRC_DIR)/%,$(OBJ_DIR)/%,$@)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(@D) $(dir $(DEP_DIR)/$*)
	$(CC) -std=$(STD) -fPIC $(CCFLAGS) $(INCLUDE) $(WARNINGS) -c -o $@ $< -MMD -MP -MF $(DEP_DIR)/$*.d -MT $@

-include $(DEP)

compile: $(OBJ)

clean:
	rm -rf $(BUILD_DIR)

.PHONY: clean compile
